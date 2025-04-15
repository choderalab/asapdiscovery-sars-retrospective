#!/usr/bin/env nextflow
include {
    CROSS_DOCK
} from "./modules.nf"

workflow {
    // Create channels from directories
    input_structures = Channel
        .fromPath("${params.curatedFragalysis}/aligned/Mpro-*", type: 'dir')
        .map { dir ->
            def id = dir.name.toString().find(/Mpro-([a-zA-Z0-9_]+)/) { match, code -> code }
//             log.info "Input structure found: ${dir.name}, ID: ${id}"
            return tuple(id, dir)
        }

    // Count input structures
    input_structures.count().view { count -> "Total input structures found: $count" }

    prepped_structures = Channel
        .fromPath("${params.dataPath}/${params.fixedFragalysisCache}/Mpro-*-*", type: 'dir')
        .map { dir ->
            def id = dir.name.toString().find(/Mpro-([a-zA-Z0-9_]+)-/) { match, code -> code }
//             log.info "Prepped structure found: ${dir.name}, ID: ${id}"
            return tuple(id, dir)
        }

    // Count prepped structures
    prepped_structures.count().view { count -> "Total prepped structures found: $count" }

    // Join the channels on the extracted ID
    paired_structures = input_structures
        .join(prepped_structures, failOnMismatch: false)
        .map { id, input_dir, prepped_dir ->
//             log.info "Paired: ${id} - Input: ${input_dir.name}, Prepped: ${prepped_dir.name}"
            return tuple(id, input_dir, prepped_dir)
        }

    // Count paired structures
    paired_structures.count().view { count -> "Total paired structures: $count" }

    // Check take parameter
    log.info "Taking ${params.take ?: 'all'} paired structures"

    // load in ligand file
    ligand_files = Channel
        .fromPath("${params.ligandFiles}/${params.split2dligandFiles}/*.sdf", type: 'file')
        .map { file ->
            def id = file.name.toString().find(/([a-zA-Z0-9_-]+)\.sdf/) { match, code -> code }
//             log.info "Prepped ligand found: ${file.name}, ID: ${id}"
            return tuple(id, file)
        }
    // Count ligand_files
    ligand_files.count().view { count -> "Total ligand files found: $count" }

    log.info "Taking ${params.take ?: 'all'} ligand files"

    // Call your process with the paired directories (handle null take parameter)
    CROSS_DOCK(paired_structures.take(params.take), ligand_files.take(params.take), "FRED", "PairwiseSelector")
    CROSS_DOCK(paired_structures.take(params.take), ligand_files.take(params.take), "POSIT", "PairwiseSelector")
}