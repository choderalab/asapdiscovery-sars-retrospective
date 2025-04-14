#!/usr/bin/env nextflow
include {
    PREP_CACHE_FOR_DOCKING
    GENERATE_LIGAND_FILES
} from "./modules.nf"

workflow {
    PREP_CACHE_FOR_DOCKING()
}
