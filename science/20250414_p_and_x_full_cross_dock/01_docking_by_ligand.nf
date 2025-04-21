#!/usr/bin/env nextflow
include {
    CROSS_DOCK_BY_LIGAND as CROSS_DOCK_BY_LIGAND_FRED
    CROSS_DOCK_BY_LIGAND as CROSS_DOCK_BY_LIGAND_POSIT
} from "./modules.nf"

workflow {
    // load in input structure dir
    input_dir = Channel.fromPath("${params.curatedFragalysis}", type: 'dir')
    cache_dir = Channel.fromPath("${params.fragalysisCache}", type: 'dir')

    // Create a channel for each ligand file and flatten it
    ligand_files = Channel
        .fromPath("${params.ligandFiles}/${params.split2dligandFiles}/*.sdf")
        .map { file ->
            def id = file.name.toString().find(/([a-zA-Z0-9_-]+)\.sdf/) { match, code -> code }
            return tuple(id, file)
        }

    // Count ligand_files
    ligand_files.count().view { count -> "Total ligand files found: $count" }

    log.info "Taking ${params.take ?: 'all'} ligand files"

    // Create combinations for parallel processing
    docking_combinations = input_dir
        .combine(cache_dir)
        .combine(ligand_files)
        .take(params.take)

    // Run FRED and POSIT docking in parallel for each combination
    CROSS_DOCK_BY_LIGAND_FRED(
        docking_combinations.map{ it[0..3] },
        "FRED",
        "PairwiseSelector"
    )

    CROSS_DOCK_BY_LIGAND_POSIT(
        docking_combinations.map{ it[0..3] },
        "ALL",
        "PairwiseSelector"
    )
}