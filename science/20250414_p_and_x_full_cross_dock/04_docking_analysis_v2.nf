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
        CREATE_EVALUATORS_TWO(name, docking_results_parquet, docking_results_json)
        CREATE_EVALUATORS_TWO.out.evaluator_json
            .flatten()
            .buffer(size: params.K)
            .set { eval_inputs_ch }

        RUN_EVALUATORS_TWO(name, docking_results_parquet, docking_results_json)
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