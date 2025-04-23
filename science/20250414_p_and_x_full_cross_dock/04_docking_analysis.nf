#!/usr/bin/env nextflow
include {
    CREATE_EVALUATORS
    RUN_EVALUATORS
    COMBINE_EVALUATIONS
} from "./modules.nf"

workflow RUN_DOCKING_ANALYSIS {
    take:
    config_tuple  // A tuple containing (id, name, results_file, settings_file)

    main:
    def name_ch = Channel.value(config_tuple[1])
    def results_ch = Channel.fromPath(config_tuple[2], checkIfExists: true)
    def settings_ch = Channel.fromPath(config_tuple[3], checkIfExists: true)

    CREATE_EVALUATORS(name_ch, results_ch, settings_ch)

    // map the number at the end of the file name as an id
    CREATE_EVALUATORS.out.evaluator_json
        .flatten()
        .buffer(size: params.K)
        .set { eval_inputs_ch }

    eval_inputs_ch
        .combine(name_ch)
        .combine(results_ch)
        .set { eval_inputs_ch }

    RUN_EVALUATORS(eval_inputs_ch)

    COMBINE_EVALUATIONS(
        name_ch,
        RUN_EVALUATORS.out.evaluator_results.collect()
    )

    emit:
    results = COMBINE_EVALUATIONS.out // Assuming COMBINE_EVALUATIONS has an output channel
}

workflow {
    // Define configurations with unique IDs
    params.all_no_sim = "${params.combinedDockingResultsPath}/ALL_combined_results_no_chemical_similarity.csv"
    params.all_sim = "${params.combinedDockingResultsPath}/ALL_combined_results.csv"
    params.fred_no_sim = "${params.combinedDockingResultsPath}/FRED_combined_results_no_chemical_similarity.csv"
    params.fred_sim = "${params.combinedDockingResultsPath}/FRED_combined_results.csv"

    params.datesplit_settings = "${params.configFiles}/settings_cross_docking_defaults.yml"
    params.multipose_settings = "${params.configFiles}/settings_multipose_split.yml"
    params.settings_scaffold_split_not_x_to_x = "${params.configFiles}/settings_scaffold_split_not_x_to_x.yml"
    params.settings_scaffold_split_x_to_x = "${params.configFiles}/settings_scaffold_split_x_to_x.yml"
    params.settings_scaffold_split_x_to_y = "${params.configFiles}/settings_scaffold_split_x_to_y.yml"
    params.settings_similarity_split_tanimotocombo = "${params.configFiles}/settings_similarity_split_tanimotocombo.yml"
    params.settings_similarity_split_ecfp = "${params.configFiles}/settings_similarity_split_ecfp.yml"
    params.settings_similarity_split_mcs = "${params.configFiles}/settings_similarity_split_mcs.yml"

    Channel
        .from([
            // [id, name, results_file_path, settings_file_path]
            ["datesplit_posit", params.all_no_sim, params.datesplit_settings],
            ["datesplit_fred", params.fred_no_sim, params.datesplit_settings],
        ])
        .set { configs }

    // Process each configuration
    RUN_DOCKING_ANALYSIS(configs)
}