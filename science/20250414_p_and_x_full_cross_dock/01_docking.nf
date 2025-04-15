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
            return tuple(id, dir)
        }

    prepped_structures = Channel
        .fromPath("${params.dataPath}/${params.fixedFragalysisCache}/Mpro-*-*", type: 'dir')
        .map { dir ->
            def id = dir.name.toString().find(/Mpro-([A-Z0-9_]+)-/) { match, code -> code }
            return tuple(id, dir)
        }

    // Join the channels on the extracted ID
    paired_structures = input_structures
        .join(prepped_structures, failOnMismatch: false)
        .map { id, input_dir, prepped_dir ->
            // Log the pairing to help with debugging
            log.info "Paired: ${id} - Input: ${input_dir.name}, Prepped: ${prepped_dir.name}"
            return tuple(id, input_dir, prepped_dir)
        }

    // Call your process with the paired directories
    CROSS_DOCK(paired_structures.take(params.take))
}