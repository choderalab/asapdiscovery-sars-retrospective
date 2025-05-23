#!/usr/bin/env nextflow
include {
    CALCULATE_RMSD_TWO
    CONVERT_TO_DOCKING_DATA_MODEL
} from "./modules.nf"

process COMBINE_AND_PROCESS_RESULTS {
    publishDir "${params.combinedDockingResultsPath}", mode: 'copy', overwrite: true
    conda "${params.asap}"
    tag "combine-and-process-results ${method}"
    errorStrategy = { task.exitStatus in [137,140,143,247] ? 'retry' : 'finish' }
    maxRetries 3
    // Dynamic memory allocation
    memory { task.attempt > 1 ? (2 ** (task.attempt - 1)) * 8.GB : 8.GB }
    // Dynamic time allocation
    time { task.attempt > 1 ? (2 ** (task.attempt - 1)) * 2.h : 2.h }

    input:
    path(dockedLigandRMSDs)
    val(name)

    output:
    path("*")

    script:
    """
    python3 "${params.scripts}"/combine_and_process_results_v2.py \
    ${dockedLigandRMSDs.join(' ')} \
    --tc-data "${params.combinedChemicalSimilarityPath}/tanimoto_combo/tanimoto_combo.csv" \
    --ecfp-data "${params.combinedChemicalSimilarityPath}/ecfp_tanimoto/fingerprint_similarities.csv" \
    --mcs-data "${params.combinedChemicalSimilarityPath}/mcs_tanimoto/mcs_tanimoto.csv" \
    --date-dict "${params.dateDictPath}" \
    --structure-cmpd-dict "${params.dataPath}/cmpd_date_dict/structure_to_cmpd_dict.json"
    --chemical-scaffold-data "${params.genericScaffoldPath}" \
    --output-file-prefix "${name} \
    --deduplicate
    """
}

workflow COMBINE_DOCKING_RESULTS {
    take:
    method

    main:
    docked_dirs = Channel
        .fromPath("${params.dockedFiles}/${method}/*docked", type: 'dir')
        .map { results_dir ->
            def id = results_dir.name.toString().find(/([a-zA-Z0-9_-]+)\_docked/) { match, code -> code }
            return tuple(method, id, results_dir)
        }
    ligand_file_3d = Channel
        .fromPath("${params.ligandFiles}/${params.ligandFile3d}", type: 'file')

    // Combine each docked directory with the ligand file
    input_pairs = docked_dirs.combine(ligand_file_3d)

    // Run CALCULATE_RMSD for each pair
    CALCULATE_RMSD_TWO(input_pairs)

    // Collect the results into a single value
    input_csvs = CALCULATE_RMSD_TWO.out.rmsd_csv.collect()

    // Convert method to a channel
    method_ch = Channel.value(method)

    COMBINE_AND_PROCESS_RESULTS(
        input_csvs,
        method_ch
    )
}

// Create named entry points for each dataset
workflow PROCESS_FRED {
    COMBINE_DOCKING_RESULTS('FRED')
}

workflow PROCESS_ALL {
    COMBINE_DOCKING_RESULTS('ALL')
}

workflow PROCESS_ALL_MULTIPOSE {
    COMBINE_DOCKING_RESULTS('ALL_multipose')
}

workflow {
    PROCESS_FRED()
    PROCESS_ALL()
}