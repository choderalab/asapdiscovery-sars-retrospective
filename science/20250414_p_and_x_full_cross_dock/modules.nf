process PREP_FRAGALYSIS {
    publishDir "${params.fragalysisCache}", mode: 'copy', overwrite: true
    conda "${params.asap}"
    tag "prep-fragalysis-${params.curatedFragalysis}"
    clusterOptions '--partition cpu --cpus-per-task=64 --mem=128G --time=24:00:00'

    script:
    """
    #!/bin/bash
    asap-cli protein-prep \
      --target SARS-CoV-2-Mpro \
      --fragalysis-dir "${params.curatedFragalysis}"\
      --loop-db ${params.loopDB} \
      --ref-chain A \
      --active-site-chain A \
      --use-dask \
      --dask-n-workers 64 \
      --dask-type local \
    """
}