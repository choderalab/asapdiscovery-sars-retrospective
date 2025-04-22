#!/usr/bin/env nextflow
include {
    CALCULATE_RMSD
    COMBINE_AND_PROCESS_RESULTS
} from "./modules.nf"

// Define input channels
Channel.empty().set { ALL_chem_sim_ch }
Channel.empty().set { FRED_chem_sim_ch }
Channel.empty().set { ALL_no_sim_ch }
Channel.empty().set { FRED_no_sim_ch }

workflow SETUP_CHANNELS {
    Channel.fromPath("${params.combinedDockingResultsPath}/ALL_combined_results.csv")
        .tap { ALL_chem_sim_ch }

    Channel.fromPath("${params.combinedDockingResultsPath}/FRED_combined_results.csv")
        .tap { FRED_chem_sim_ch }


    Channel.fromPath("${params.combinedDockingResultsPath}/ALL_combined_results_no_chemical_similarity.csv")
        .tap { ALL_no_sim_ch }

    Channel.fromPath("${params.combinedDockingResultsPath}/FRED_combined_results_no_chemical_similarity.csv")
        .tap { FRED_no_sim_ch }

// Define analysis workflow
include {
    CREATE_EVALUATORS
    RUN_EVALUATORS
    COMBINE_EVALUATIONS
} from "./modules.nf"

workflow DATASETSPLIT_ANALYSIS {
    // Load Settings
    settings_file = Channel
        .fromPath("${params.configFiles}/settings_cross_docking_defaults.yml", type: 'file')
    name = Channel.value("datesplit")
    // Use the shared channel
    CREATE_EVALUATORS(name, ALL_no_sim_ch, settings_file)

    // Combine channels in the correct order for the process
    eval_inputs_ch = CREATE_EVALUATORS.out.evaluator_json
    .combine(name)
    .combine(ALL_no_sim_ch)

    RUN_EVALUATORS(eval_inputs_ch)

    COMBINE_EVALUATIONS(
        name,
        RUN_EVALUATORS.out.evaluator_results.collect()
    )
}

workflow {
    DATASETSPLIT_ANALYSIS()
}