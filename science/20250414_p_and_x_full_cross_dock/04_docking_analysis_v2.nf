#!/usr/bin/env nextflow
include {
    CREATE_EVALUATORS_TWO
    RUN_EVALUATORS_TWO
    COMBINE_EVALUATIONS
} from "./modules.nf"

workflow RUN_DOCKING_ANALYSIS {
    take:
        name
        docking_results_parquet
        docking_results_json

    main:
        evaluator_settings = Channel.fromPath("${params.evaluator_configs}/*.yaml", type: 'file')
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
            evaluator_results.evaluator_json_directory
        )

        COMBINE_EVALUATIONS(
            name,
            RUN_EVALUATORS_TWO.out.evaluator_results.collect()
        )
}

workflow RUN_DOCKING_ANALYSIS_POSIT {
    RUN_DOCKING_ANALYSIS("all_evals_posit", params.all_sim_parquet, params.all_sim_json)
}
workflow RUN_DOCKING_ANALYSIS_FRED {
    RUN_DOCKING_ANALYSIS("all_evals_fred", params.all_sim_parquet, params.all_sim_json)
}
workflow {
    RUN_DOCKING_ANALYSIS_FRED()
    RUN_DOCKING_ANALYSIS_POSIT()
}