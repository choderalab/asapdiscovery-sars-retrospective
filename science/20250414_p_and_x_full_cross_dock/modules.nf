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
    python3 ${params.scripts}/split_sdf.py --sdf_fn ${ligandFile3d} --out_dir ${params.split3dligandFiles} --chunk_size 1 --name_convention "integer"
    python3 ${params.scripts}/split_sdf.py --sdf_fn ${ligandFile2d} --out_dir ${params.split2dligandFiles} --chunk_size 1 --name_convention "integer"
    """
}
process CROSS_DOCK {
    publishDir "${params.dockedFiles}/${posit_method}", mode: 'link', overwrite: true
    conda "${params.asap}"
    tag "cross-dock ${structure_name} ${compound_name}"
    clusterOptions '--partition "cpushort" --time=00:10:00 --mem 4G'
    errorStrategy { task.exitStatus == 140 ? 'retry' : 'ignore' } // retry if the task is killed bc out of memory or time, otherwise ignore and move on

    // Dynamic memory allocation
    memory { task.attempt > 1 ? (2 ** (task.attempt - 1)) * 8.GB : 8.GB }

    // Dynamic time allocation
    time { task.attempt > 1 ? (2 ** (task.attempt - 1)) * 2.h : 2.h }

    input:
    tuple val(structure_name), path(input_dir), path(prepped_dir), val(compound_name), path(ligandFile2d)
    val posit_method
    val selector

    output:
    path("*_docked"), emit: docked

    script:
    """
    asap-cli docking cross-docking \
    --target SARS-CoV-2-Mpro \
    --use-omega \
    --omega-dense \
    --allow-retries \
    --allow-final-clash \
    --relax-mode clash \
    --posit-method "${posit_method}" \
    --structure-selector "${selector}" \
    --structure-dir ${input_dir} \
    --ligands "${ligandFile2d}" \
    --cache-dir "${prepped_dir}" \
    --output-dir "${structure_name}_${compound_name}_docked" \
    --overwrite \
    --no-save-to-cache \
    --use-only-cache \
    --num-poses "${params.numPoses}" \
    """
}
process CROSS_DOCK_BY_STRUCTURE {
    publishDir "${params.dockedFiles}/${posit_method}", mode: 'link', overwrite: true
    conda "${params.asap}"
    tag "cross-dock ${structure_name}"
    clusterOptions '--partition "cpu" --time=04:00:00 --mem=256GB --cpus-per-task=32'
    errorStrategy { task.exitStatus == 140 ? 'retry' : 'ignore' } // retry if the task is killed bc out of memory or time, otherwise ignore and move on

    // Dynamic memory allocation
    memory { task.attempt > 1 ? (2 ** (task.attempt - 1)) * 8.GB : 8.GB }

    // Dynamic time allocation
    time { task.attempt > 1 ? (2 ** (task.attempt - 1)) * 2.h : 2.h }

    input:
    tuple val(structure_name), path(input_dir), path(prepped_dir), path(ligand_file_2d)
    val posit_method
    val selector

    output:
    path("*_docked"), emit: docked

    script:
    """
    asap-cli docking cross-docking \
    --target SARS-CoV-2-Mpro \
    --use-omega \
    --omega-dense \
    --allow-retries \
    --allow-final-clash \
    --relax-mode clash \
    --posit-method "${posit_method}" \
    --structure-selector "${selector}" \
    --structure-dir ${input_dir} \
    --ligands "${ligand_file_2d}" \
    --cache-dir "${prepped_dir}" \
    --output-dir "${structure_name}_docked" \
    --overwrite \
    --no-save-to-cache \
    --use-only-cache \
    --num-poses "${params.numPoses}" \
    --use-dask \
    --dask-type local \
    --dask-n-workers 32
    """
}
process CROSS_DOCK_BY_LIGAND {
    publishDir "${params.dockedFiles}/${posit_method}", mode: 'link', overwrite: true
    conda "${params.asap}"
    tag "cross-dock ${compound_name}"
    clusterOptions '--partition "cpu" --time=04:00:00 --mem=256GB --cpus-per-task=32'
    errorStrategy { task.exitStatus == 140 ? 'retry' : 'ignore' } // retry if the task is killed bc out of memory or time, otherwise ignore and move on

    // Dynamic memory allocation
    memory { task.attempt > 1 ? (2 ** (task.attempt - 1)) * 8.GB : 8.GB }

    // Dynamic time allocation
    time { task.attempt > 1 ? (2 ** (task.attempt - 1)) * 2.h : 2.h }

    input:
    tuple path(input_dir), path(prepped_dir), val(compound_name), path(ligandFile2d)
    val posit_method
    val selector

    output:
    path("*_docked"), emit: docked

    script:
    """
    asap-cli docking cross-docking \
    --target SARS-CoV-2-Mpro \
    --use-omega \
    --omega-dense \
    --allow-retries \
    --allow-final-clash \
    --relax-mode clash \
    --posit-method "${posit_method}" \
    --structure-selector "${selector}" \
    --fragalysis-dir ${input_dir} \
    --ligands "${ligandFile2d}" \
    --cache-dir "${prepped_dir}" \
    --output-dir "${compound_name}_docked" \
    --overwrite \
    --no-save-to-cache \
    --use-only-cache \
    --num-poses "${params.numPoses}" \
    --use-dask \
    --dask-type local \
    --dask-n-workers 32
    """
}

process GENERATE_DATE_DICTIONARY {
    publishDir "${params.dataPath}", mode: 'copy', overwrite: true
    conda "${params.asap}"
    tag "generate-date-dictionary"

    output:
    path "cmpd_date_dict"
    path "cmpd_date_dict/date_dict.json", emit: structure_to_date_dict
    path "cmpd_date_dict/structure_to_cmpd_dict.json", emit: structure_to_cmpd_dict

    script:
    """
    python3 "${params.scripts}"/generate_date_dict.py --fragalysis-dir "${params.curatedFragalysis}" --output-dir cmpd_date_dict
    """
}
process CALCULATE_ECFP_TANIMOTO {
    publishDir "${params.chemicalSimilarityData}", mode: 'copy', overwrite: true
    conda "${params.asap}"
    tag "calculate-ecfp-tanimoto"

    input:
    path(ligand_file_3d)

    output:
    path("ecfp_tanimoto"), emit: ecfp_tanimoto

    script:
    """
    python3 "${params.scripts}"/calculate_ecfp_tanimoto.py --ref-ligand-sdf "${ligand_file_3d}" --output-dir ecfp_tanimoto
    """
}
process CALCULATE_MCS_TANIMOTO {
    publishDir "${params.chemicalSimilarityData}", mode: 'copy', overwrite: true
    conda "${params.asap}"
    tag "calculate-mcs-tanimoto"
    clusterOptions '--partition "cpu" --time=24:00:00 --mem=64GB --cpus-per-task=32'

    input:
    path(ligand_file_3d)

    output:
    path("mcs_tanimoto"), emit: mcs_tanimoto

    script:
    """
    python3 "${params.scripts}"/calculate_mcs_tanimoto.py --ref-ligand-sdf "${ligand_file_3d}" --output-dir mcs_tanimoto --ncpus 32
    """
}
process CALCULATE_TANIMOTO_COMBO {
    publishDir "${params.chemicalSimilarityData}", mode: 'copy', overwrite: true
    conda "${params.asap}"
    tag "calculate-tanimoto-combo"
    clusterOptions '--partition "cpu" --time=06:00:00 --mem=64GB --cpus-per-task=32'

    input:
    path(ligand_file_3d)

    output:
    path("tanimoto_combo"), emit: tanimoto_combo

    script:
    """
    python3 "${params.scripts}"/calculate_tanimoto_combo.py --ref-ligand-sdf "${ligand_file_3d}" --output-dir tanimoto_combo
    """
}
process COMBINE_CHEMICAL_SIMILARITY_DATA {
    publishDir "${params.chemicalSimilarityData}", mode: 'copy', overwrite: true
    conda "${params.asap}"
    tag "combine-chemical-similarity-data"

    input:
    path csv_files

    output:
    path "combined_chemical_similarity_data.csv", emit: combined_chemical_similarity_data

    script:
    """
    python3 "${params.scripts}/combine_chemical_similarity_data.py" ${csv_files.join(' ')}
    """
}
process RUN_BEMIS_MURCKO_CLUSTERING {
    publishDir "${params.chemicalSimilarityData}", mode: 'copy', overwrite: true
    conda "${params.asap}"
    tag "run-bemis-murcko-clustering"

    input:
    path(ligand_file_2d)

    output:
    path "${params.scaffoldDataName}", emit: bemis_murcko_clustering

    script:
    """
    python "${params.scripts}"/run_bemis_murcko_clustering.py --sdf-2d ${ligand_file_2d} --output-dir "${params.scaffoldDataName}
    """
}
process CALCULATE_RMSD {
    conda "${params.asap}"
    tag "calculate-rmsds ${uuid}"
    label 'cpushort'

    input:
    tuple val(method), val(uuid), path(docked_dir), path(ligand_file_3d)

    output:
    path("*.csv"), emit: rmsd_csv

    script:
    """
    python3 "${params.scripts}"/calculate_rmsd_from_docking_results.py \
    -d "${docked_dir}" \
    -l "${ligand_file_3d}" \
    -o "${method}_${uuid}_rmsd_results.csv"
    """
}
process COMBINE_AND_PROCESS_RESULTS {
    publishDir "${params.dataPath}", mode: 'copy', overwrite: true, saveAs: {fn -> "${params.combinedDockingResults}"}
    conda "${params.asap}"
    tag "combine-and-process-results"
    errorStrategy = { task.exitStatus in [137,140,143,247] ? 'retry' : 'finish' }
    maxRetries 3
    // Dynamic memory allocation
    memory { task.attempt > 1 ? (2 ** (task.attempt - 1)) * 8.GB : 8.GB }
    // Dynamic time allocation
    time { task.attempt > 1 ? (2 ** (task.attempt - 1)) * 2.h : 2.h }

    input:
    path(dockedLigandRMSDs)
    path(fixedFragalysisCache)
    path(chemicalSimilarityData)
    path(structure_to_date_dict)
    path(chemical_scaffold_data)

    output:
    path("combined_results"), emit: combined_results

    script:
    """
    python3 "${params.scripts}"/combine_and_process_results.py \
    --input-csvs ${dockedLigandRMSDs.join(' ')} \
    --protein-cache "${fixedFragalysisCache}" \
    --ligand-cache "${fixedFragalysisCache}" \
    --data-path "${chemicalSimilarityData}" \
    --date-dict "${structure_to_date_dict}" \
    --combined-chemical-similarity-csv "${chemical_scaffold_data}" \
    --output-dir combined_results \
    --output-file-name combined_results.csv \
    --add-padding
    """

}