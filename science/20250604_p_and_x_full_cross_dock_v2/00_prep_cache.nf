#!/usr/bin/env nextflow
include {
    PREP_CACHE_FOR_DOCKING
    GENERATE_COMBINED_LIGAND_FILES
    GENERATE_SPLIT_LIGAND_FILES
} from "./modules.nf"

workflow {
    cache_ch = Channel.fromPath("${params.fragalysisCache}", type: 'dir', checkIfExists: true)
    PREP_CACHE_FOR_DOCKING(cache_ch)
    GENERATE_COMBINED_LIGAND_FILES(PREP_CACHE_FOR_DOCKING.out.fixed_cache)
    GENERATE_SPLIT_LIGAND_FILES(GENERATE_COMBINED_LIGAND_FILES.out.ligandFile3d, GENERATE_COMBINED_LIGAND_FILES.out.ligandFile2d)
}
