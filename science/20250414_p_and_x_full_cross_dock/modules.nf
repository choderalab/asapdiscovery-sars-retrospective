process PREP_FRAGALYSIS {
    publishDir "${params.dataPath}", mode: 'copy', overwrite: true, saveAs: {fn -> "${params.fragalysisCache}"}
    conda "${params.asap}"
    tag "prep-fragalysis"
    clusterOptions '-c 32 --mem=128G --time=04:00:00'

    input:
    path curatedFragalysis

    output:
    path("output"), emit: fragalysisCache

    script:
    """
    asap-cli protein-prep \
      --target SARS-CoV-2-Mpro \
      --fragalysis-dir "${curatedFragalysis}" \
      --loop-db ${params.loopDB} \
      --ref-chain A \
      --active-site-chain A \
      --use-dask \
      --dask-n-workers 32 \
      --dask-type local \
    """
}
process PREP_CACHE_FOR_DOCKING {
    publishDir "${params.dataPath}", mode: 'copy', overwrite: true, saveAs: {fn -> "${params.fixedFragalysisCache}"}
    conda "${params.asap}"
    tag "prep-cache-for-docking"
    label 'local'

    input:
    path cache_dir

    output:
    path "*_fixed", emit: fixed_cache

    script:
    """
    python3 "${params.scripts}"/prep_cache_for_docking.py --input_cache "${cache_dir}"
    """
}
process GENERATE_COMBINED_LIGAND_FILES {
    publishDir "${params.ligandFiles}", mode: 'copy', overwrite: true
    conda "${params.asap}"
    tag "generate-ligand-files"
    label 'local'

    input:
    path cache_dir

    output:
    path "${params.ligandFile3d}", emit: ligandFile3d
    path "${params.ligandFile2d}", emit: ligandFile2d

    script:
    """
    python3 ${params.scripts}/combined_sdf_from_cache.py --input_cache "${cache_dir}"
    python3 ${params.scripts}/combined_sdf_from_cache.py --input_cache "${cache_dir}" --flatten
    """
}
process GENERATE_SPLIT_LIGAND_FILES {
    publishDir "${params.ligandFiles}", mode: 'copy', overwrite: true
    conda "${params.asap}"
    tag "generate-ligand-files"
    label 'local'

    input:
    path(ligandFile3d)
    path(ligandFile2d)

    output:
    path "${params.split3dligandFiles}", emit: split3dligandFiles
    path "${params.split2dligandFiles}", emit: split2dligandFiles

    script:
    """
    python3 ${params.scripts}/split_sdf.py --sdf_fn ${ligandFile3d} --out_dir ${params.split3dligandFiles} --chunk_size 1 --name_convention "name"
    python3 ${params.scripts}/split_sdf.py --sdf_fn ${ligandFile2d} --out_dir ${params.split2dligandFiles} --chunk_size 1 --name_convention "name"
    """
}
process CROSS_DOCK {
    publishDir "${params.dockedFiles}", mode: 'link', overwrite: true
    conda "${params.asap}"
    tag "cross-dock ${uuid}"
    clusterOptions '--partition "cpushort" --time=00:10:00 --mem 4G'

    input:
    tuple val(structure_name), path(input_dir), path(prepped_dir)
    tuple val(compound_name), path(ligandFile2d)

    output:
    path("./"), emit: docked

    script:
    """
    asap-cli docking cross-docking \
    --target SARS-CoV-2-Mpro \
    --use-omega \
    --omega-dense \
    --allow-retries \
    --allow-final-clash \
    --relax-mode clash \
    --posit-method FRED \
    --structure-selector PairwiseSelector \
    --structure-dir ${input_dir} \
    --ligands "${ligandFile2d}" \
    --cache-dir "${prepped_dir}" \
    --output-dir "${structure_name}_${compound_name}" \
    --overwrite \
    --no-save-to-cache \
    --use-only-cache \
    --num-poses 50 \
    --use-dask \
    --dask-type local \
    --dask-n-workers 1
    """

}
