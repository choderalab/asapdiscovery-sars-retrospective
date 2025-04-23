#!/usr/bin/env nextflow

process DATESPLIT_POSIT {
    label 'figure'
    script:
    """
    python ${params.scripts}/plotting.py \
        plot-filled-in-error-bars \
        ${params.datesplitPositResults} \
        --fig-name datesplit_posit
    """
}

process CHEMICAL_SIMILARITY_ECDF {
    label 'figure'
    script:
    """
    python ${params.scripts}/plotting.py \
        plot-chemical-similarity-ecdf \
        ${params.combinedChemicalSimilarityPath} \
        --fig-name chemical_similarity_ecdf
    """

}

workflow {
    DATESPLIT_POSIT()
}