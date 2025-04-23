#!/usr/bin/env nextflow
include {
    CREATE_EVALUATORS
    RUN_EVALUATORS
    COMBINE_EVALUATIONS
} from "./modules.nf"

workflow RUN_DOCKING_ANALYSIS {
    take:
    config_tuple  // A tuple containing (name, results_file, settings_file)

    main:
    name = config_tuple[0]
    docking_results = config_tuple[1]
    settings = config_tuple[2]

//     config_tuple.view()


    CREATE_EVALUATORS(name_ch, docking_results, settings)

    CREATE_EVALUATORS.out.evaluator_json
        .flatten()
        .buffer(size: params.K)
        .set { eval_inputs_ch }

//     eval_inputs_ch.first().view()

    RUN_EVALUATORS(name, docking_results, eval_inputs_ch)

    COMBINE_EVALUATIONS(
        name,
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
        .fromList([
            // [id, name, results_file_path, settings_file_path]
            ["datesplit_posit", params.all_no_sim, params.datesplit_settings],
            ["datesplit_fred", params.fred_no_sim, params.datesplit_settings],
        ])
        .set { configs }

    // Process each configuration
    RUN_DOCKING_ANALYSIS(configs)
}