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
    Channel.fromPath("${params.combinedDockingResultsPath}/ALL_combined_results.csv", checkIfExists: true)
        .tap { ALL_chem_sim_ch }

    Channel.fromPath("${params.combinedDockingResultsPath}/FRED_combined_results.csv", checkIfExists: true)
        .tap { FRED_chem_sim_ch }

    Channel.fromPath("${params.combinedDockingResultsPath}/ALL_combined_results_no_chemical_similarity.csv", checkIfExists: true)
        .tap { ALL_no_sim_ch }

    Channel.fromPath("${params.combinedDockingResultsPath}/FRED_combined_results_no_chemical_similarity.csv", checkIfExists: true)
        .tap { FRED_no_sim_ch }
}

// Define analysis workflow
include {
    CREATE_EVALUATORS
    RUN_EVALUATORS
    COMBINE_EVALUATIONS
} from "./modules.nf"

workflow DATASETSPLIT_ANALYSIS {
    take:
        all_no_sim

    main:
    // Load Settings
    settings_file = Channel
        .fromPath("${params.configFiles}/settings_cross_docking_defaults.yml", type: 'file')
    name = Channel.value("datesplit")

    // Use the input channel
    CREATE_EVALUATORS(name, all_no_sim, settings_file)

    // Combine channels in the correct order for the process
    eval_inputs_ch = CREATE_EVALUATORS.out.evaluator_json
        .combine(name)
        .combine(all_no_sim)

    RUN_EVALUATORS(eval_inputs_ch)

    COMBINE_EVALUATIONS(
        name,
        RUN_EVALUATORS.out.evaluator_results.collect()
    )
}

workflow {
    // First run the setup to populate the channels
    SETUP_CHANNELS()

    ALL_chem_sim_ch.view{
        "All with chemical similarity: ${it}"
    }

    // Then run the analysis with the populated channel
    DATASETSPLIT_ANALYSIS(ALL_no_sim_ch)
}