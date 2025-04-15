#!/usr/bin/env nextflow
include {
    CROSS_DOCK
} from "./modules.nf"

workflow {
    // Create channels from directories
    input_structures = Channel
        .fromPath("${params.curatedFragalysis}/Mpro-*", type: 'dir')
        .map { dir ->
            def id = dir.name.toString().find(/Mpro-([A-Z0-9_]+)/) { match, code -> code }
            log.info "Input structure found: ${dir.name}, ID: ${id}"
            return tuple(id, dir)
        }

    // Count input structures
    input_structures.count().view { count -> "Total input structures found: $count" }

    prepped_structures = Channel
        .fromPath("${params.dataPath}/${params.fixedFragalysisCache}/Mpro-*-*", type: 'dir')
        .map { dir ->
            def id = dir.name.toString().find(/Mpro-([A-Z0-9_]+)-/) { match, code -> code }
            log.info "Prepped structure found: ${dir.name}, ID: ${id}"
            return tuple(id, dir)
        }

    // Count prepped structures
    prepped_structures.count().view { count -> "Total prepped structures found: $count" }

    // Join the channels on the extracted ID
    paired_structures = input_structures
        .join(prepped_structures, failOnMismatch: false)
        .map { id, input_dir, prepped_dir ->
            log.info "Paired: ${id} - Input: ${input_dir.name}, Prepped: ${prepped_dir.name}"
            return tuple(id, input_dir, prepped_dir)
        }

    // Count paired structures
    paired_structures.count().view { count -> "Total paired structures: $count" }

    // Check take parameter
    log.info "Taking ${params.take ?: 'all'} paired structures"

    // Call your process with the paired directories (handle null take parameter)
    if (params.take) {
        CROSS_DOCK(paired_structures.take(params.take))
    } else {
        CROSS_DOCK(paired_structures)
    }
}