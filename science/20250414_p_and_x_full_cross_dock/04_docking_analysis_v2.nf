#!/usr/bin/env nextflow
include {
    CREATE_EVALUATORS_TWO
    RUN_EVALUATORS
    COMBINE_EVALUATIONS
} from "./modules.nf"

workflow RUN_DOCKING_ANALYSIS_POSIT {
    CREATE_EVALUATORS_TWO("all_evals_posit", params.all_sim_parquet)
    CREATE_EVALUATORS.out.evaluator_json
        .flatten()
        .buffer(size: params.K)
        .set { eval_inputs_ch }

    RUN_EVALUATORS(name, params.all_sim_parquet, eval_inputs_ch)
    COMBINE_EVALUATIONS(
        name,
        RUN_EVALUATORS.out.evaluator_results.collect()
    )
}
workflow RUN_DOCKING_ANALYSIS_FRED {
    CREATE_EVALUATORS_TWO("all_evals_posit", params.all_sim_parquet)
    CREATE_EVALUATORS.out.evaluator_json
        .flatten()
        .buffer(size: params.K)
        .set { eval_inputs_ch }

    RUN_EVALUATORS(name, params.all_sim_parquet, eval_inputs_ch)
    COMBINE_EVALUATIONS(
        name,
        RUN_EVALUATORS.out.evaluator_results.collect()
    )
}