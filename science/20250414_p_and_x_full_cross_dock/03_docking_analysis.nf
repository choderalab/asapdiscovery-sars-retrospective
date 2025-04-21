#!/usr/bin/env nextflow
include {
    CALCULATE_RMSD_ARRAY
    COMBINE_AND_PROCESS_RESULTS
} from "./modules.nf"

workflow {
    // Create channels from directories for docked directories and ligand_file_3d
    docked_dirs = Channel
        .fromPath("${params.dockedFiles}/*/*docked", type: 'dir')

    ligand_file_3d = Channel
        .fromPath("${params.ligandFiles}/${params.ligandFile3d}", type: 'file')

    // Combine each docked directory with the ligand file
    docked_dirs
        .combine(ligand_file_3d)
        .set { input_pairs }

    // Run CALCULATE_RMSD_ARRAY for each pair
    CALCULATE_RMSD_ARRAY(input_pairs)
}