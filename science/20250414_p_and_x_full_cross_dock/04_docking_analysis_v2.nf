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

        // Create channel from JSON files only after evaluator creation is complete
        // this allows resume to only re-run newly made json files while also forcing it to wait
        // for CREATE_EVALUATORS_TWO to complete
        CREATE_EVALUATORS_TWO.output.evaluator_json_directory
            .map { dir -> Channel.fromPath("${dir}/*.json") }
            .flatten()
            .buffer(size: params.K)
            .set { eval_inputs_ch }

        RUN_EVALUATORS_TWO(name, docking_results_parquet, docking_results_json, eval_inputs_ch)
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