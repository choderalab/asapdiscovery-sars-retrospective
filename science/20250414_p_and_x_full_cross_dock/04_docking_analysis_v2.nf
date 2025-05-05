#!/usr/bin/env nextflow
include {
    CREATE_EVALUATOR_FACTORY_SETTINGS
    CREATE_EVALUATORS_TWO
    RUN_EVALUATORS_TWO
    COMBINE_EVALUATIONS
} from "./modules.nf"

workflow RUN_DOCKING_ANALYSIS {
    take:
        name
        docking_results_parquet
        docking_results_json
        evaluator_settings

    main:
//         evaluator_settings = Channel.fromPath("${params.evaluator_configs}/*.yaml", type: 'file')
        CREATE_EVALUATORS_TWO(
            name,
            evaluator_settings,
            docking_results_parquet,
            docking_results_json
        )

        // Create channel from JSON files only after evaluator creation
        eval_inputs_ch = CREATE_EVALUATORS_TWO.output.evaluator_json_directory
            .flatMap { dir -> file("${dir}/*.json") }
            .buffer(size: params.K)

        RUN_EVALUATORS_TWO(
            name,
            docking_results_parquet,
            docking_results_json,
            eval_inputs_ch,
        )

        // Collect all evaluator results before combining
        all_results = RUN_EVALUATORS_TWO.output.evaluator_results
            .flatten()
            .collect()

        COMBINE_EVALUATIONS(
            name,
            all_results
        )
}

workflow RUN_DOCKING_ANALYSIS_POSIT {
    take:
        evaluator_settings
    main:
        RUN_DOCKING_ANALYSIS("all_evals_posit", params.all_sim_parquet, params.all_sim_json, evaluator_settings)
}
workflow RUN_DOCKING_ANALYSIS_FRED {
    take:
        evaluator_settings
    main:
        RUN_DOCKING_ANALYSIS("all_evals_fred", params.fred_sim_parquet, params.fred_sim_json, evaluator_settings)
}
workflow {
    CREATE_EVALUATOR_FACTORY_SETTINGS()
    settings_ch = CREATE_EVALUATOR_FACTORY_SETTINGS.output.evaluator_configs.flatten()
    RUN_DOCKING_ANALYSIS_FRED(settings_ch)
    RUN_DOCKING_ANALYSIS_POSIT(settings_ch)
}