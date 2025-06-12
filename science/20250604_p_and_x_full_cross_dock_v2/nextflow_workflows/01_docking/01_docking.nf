#!/usr/bin/env nextflow
include {
    CROSS_DOCK_BY_LIGAND
} from "./modules.nf"
params.take = 2
params.test_cache = "/data1/choderaj/paynea/asap-datasets/full_cross_dock/mpro_fragalysis-04-01-24_curated_cache_fixed_test"
params.test_dir = "/data1/choderaj/paynea/asap-datasets/full_cross_dock/mpro_fragalysis-04-01-24_curated_test"

workflow RUN_LIGAND_DOCKING {
    take:
        num_poses
        posit_method
        pairwise_selector

    main:
    // load in input structure dir
    // input_dir = Channel.fromPath("${params.curatedFragalysis}", type: 'dir')
    input_dir = Channel.fromPath("${params.test_dir}", type: 'dir')
//     cache_dir = Channel.fromPath("${params.dataPath}/${params.fixedFragalysisCache}", type: 'dir')
    cache_dir = Channel.fromPath("${params.test_cache}", type: 'dir')

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

//     Run FRED and POSIT docking in parallel for each combination
    CROSS_DOCK_BY_LIGAND(
        docking_combinations,
        posit_method,
        pairwise_selector
    )
}

workflow POSIT_MULTIPOSE {
    RUN_LIGAND_DOCKING(
        num_poses: 50,
        posit_method: 'ALL',
        pairwise_selector: 'PairwiseSelector'
    )
}

workflow FRED_SINGLE_POSE {
    RUN_LIGAND_DOCKING(
        num_poses: 1,
        posit_method: 'FRED',
        pairwise_selector: 'PairwiseSelector'
    )
}

workflow {
    // Run workflows
    POSIT_MULTIPOSE()
    FRED_SINGLE_POSE()
}