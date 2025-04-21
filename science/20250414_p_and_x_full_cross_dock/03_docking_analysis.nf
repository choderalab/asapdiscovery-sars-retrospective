#!/usr/bin/env nextflow
include {
    CALCULATE_RMSD_ARRAY
    COMBINE_AND_PROCESS_RESULTS
    CREATE_EVALUATORS
    RUN_EVALUATORS
    COMBINE_EVALUATOR_RESULTS
} from "./modules.nf"

workflow {
    // Create channels from directories for docked directories and ligand_file_3d
    docked_dirs = Channel
        .fromPath("${params.dockedFiles}/*/Mpro*", type: 'dir')

    ligand_file_3d = Channel
        .fromPath("${params.ligandFiles}/${params.ligandFile3d}", type: 'file')

    CALCULATE_RMSD_ARRAY(docked_dirs,ligand_file_3d)
    }