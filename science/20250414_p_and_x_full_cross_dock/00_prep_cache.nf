#!/usr/bin/env nextflow
include {
    PREP_CACHE_FOR_DOCKING
    GENERATE_COMBINED_LIGAND_FILES
    GENERATE_SPLIT_LIGAND_FILES
} from "./modules.nf"

workflow {
    cache_ch = Channel.fromPath("${params.fragalysisCache}", type: 'dir')
    PREP_CACHE_FOR_DOCKING(cache_ch)
    GENERATE_COMBINED_LIGAND_FILES()
    GENERATE_SPLIT_LIGAND_FILES(GENERATE_COMBINED_LIGAND_FILES.out.ligandFile3d, GENERATE_COMBINED_LIGAND_FILES.out.ligandFile2d)
}
