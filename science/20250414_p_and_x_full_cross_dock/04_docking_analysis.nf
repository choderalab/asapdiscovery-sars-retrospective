#!/usr/bin/env nextflow
include {
    CREATE_EVALUATORS
    RUN_EVALUATORS
    COMBINE_EVALUATIONS
} from "./modules.nf"

workflow RUN_DOCKING_ANALYSIS {
    take:
    name
    docking_results
    settings

    main:
    CREATE_EVALUATORS(name, docking_results, settings)

    CREATE_EVALUATORS.out.evaluator_json
        .flatten()
        .buffer(size: params.K)
        .set { eval_inputs_ch }

    RUN_EVALUATORS(name, docking_results, eval_inputs_ch)

    COMBINE_EVALUATIONS(
        name,
        RUN_EVALUATORS.out.evaluator_results.collect()
    )

    emit:
    results = COMBINE_EVALUATIONS.out
}

// Define analysis configurations
def analyses = [
    datesplit_posit: [
        results: params.all_no_sim,
        settings: params.datesplit_settings
    ],
    datesplit_fred: [
        results: params.fred_no_sim,
        settings: params.datesplit_settings
    ],
    multipose_posit: [
        results: params.all_no_sim,
        settings: params.multipose_settings
    ],
    multipose_fred: [
        results: params.fred_no_sim,
        settings: params.multipose_settings
    ],
    not_x_to_x_posit: [
        results: params.all_no_sim,
        settings: params.settings_scaffold_split_not_x_to_x
    ],
    x_to_not_x_posit: [
        results: params.all_no_sim,
        settings: params.settings_scaffold_split_x_to_not_x
    ]
    x_to_y_posit: [
        results: params.all_no_sim,
        settings: params.settings_scaffold_split_x_to_y
    ],
]

// Create workflows dynamically
analyses.each { name, config ->
    workflow {
        RUN_DOCKING_ANALYSIS(name, config.results, config.settings)
    }
}