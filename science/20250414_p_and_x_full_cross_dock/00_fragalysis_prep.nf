#!/usr/bin/env nextflow
include {
    PREP_FRAGALYSIS
} from "./modules.nf"

workflow {
    PREP_FRAGALYSIS()
}
