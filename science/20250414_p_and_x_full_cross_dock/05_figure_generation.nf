#!/usr/bin/env nextflow

process DATESPLIT_POSIT {
    publishDir "${params.figuresPath}", mode: 'copy', overwrite: true

    output:
    file("*.png")
    file("*.svg")

    script:
    """
    python ${params.scripts}/plotting.py \
        plot-filled-in-error-bars \
        --raw-df ${params.datesplitPositResults} \
        --fig-name datesplit_posit
    """
}

workflow {
    DATESPLIT_POSIT()
}