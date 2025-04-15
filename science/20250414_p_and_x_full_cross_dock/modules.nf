process PREP_FRAGALYSIS {
    publishDir "${params.fragalysisCache}", mode: 'copy', overwrite: true
    conda "${params.asap}"
    tag "prep-fragalysis"
    clusterOptions '-c 32 --mem=128G --time=24:00:00'

    script:
    """
    asap-cli protein-prep \
      --target SARS-CoV-2-Mpro \
      --fragalysis-dir "${params.curatedFragalysis}" \
      --loop-db ${params.loopDB} \
      --ref-chain A \
      --active-site-chain A \
      --use-dask \
      --dask-n-workers 32 \
      --dask-type local \
    """
}
process PREP_CACHE_FOR_DOCKING {
    publishDir "${params.fragalysisCache}", mode: 'copy', overwrite: true
    conda "${params.asap}"
    tag "prep-cache-for-docking"

    script:
    """
    python3 "${params.scripts}"/prep_cache_for_docking.py --input_cache "${params.fragalysisCache}"
    """
}
process GENERATE_LIGAND_FILES {
    publishDir "${params.ligandFiles}", mode: 'copy', overwrite: true
    conda "${params.asap}"
    tag "generate-ligand-files"

    script:
    """
    python3 ${params.scripts}/combined_sdf_from_cache.py --input_cache "${params.fragalysisCache}"
    python3 ${params.scripts}/combined_sdf_from_cache.py --input_cache "${params.fragalysisCache}" --flatten
    python3 ${params.scripts}/split_sdf.py --sdf_fn ${params.ligandFile3d} --out_dir ${params.split3dligandFiles} --chunk_size 1 --name_convention "integer"
    python3 ${params.scripts}/split_sdf.py --sdf_fn ${params.ligandFile2d} --out_dir ${params.split2dligandFiles} --chunk_size 1 --name_convention "integer"
    """
}