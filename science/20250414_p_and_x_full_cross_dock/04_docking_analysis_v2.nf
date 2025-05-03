#!/usr/bin/env nextflow
include {
    CREATE_EVALUATORS_TWO
    RUN_EVALUATORS_TWO
    COMBINE_EVALUATIONS
} from "./modules.nf"

workflow RUN_DOCKING_ANALYSIS_POSIT {
    name = "all_evals_posit"
    CREATE_EVALUATORS_TWO(name, params.all_sim_parquet)
    CREATE_EVALUATORS_TWO.out.evaluator_json
        .flatten()
        .buffer(size: params.K)
        .set { eval_inputs_ch }

    RUN_EVALUATORS_TWO(name, params.all_sim_parquet, eval_inputs_ch)
    COMBINE_EVALUATIONS(
        name,
        RUN_EVALUATORS_TWO.out.evaluator_results.collect()
    )
}
workflow RUN_DOCKING_ANALYSIS_FRED {
    name = "all_evals_fred"
    CREATE_EVALUATORS_TWO(name, params.all_sim_parquet)
    CREATE_EVALUATORS_TWO.out.evaluator_json
        .flatten()
        .buffer(size: params.K)
        .set { eval_inputs_ch }

    RUN_EVALUATORS_TWO(name, params.all_sim_parquet, eval_inputs_ch)
    COMBINE_EVALUATIONS(
        name,
        RUN_EVALUATORS_TWO.out.evaluator_results.collect()
    )
}
workflow {
    RUN_DOCKING_ANALYSIS_FRED()
    RUN_DOCKING_ANALYSIS_POSIT()
}