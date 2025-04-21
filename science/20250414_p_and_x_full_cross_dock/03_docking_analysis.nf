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
    docked_dirs =