#!/usr/bin/env nextflow
include {
    CREATE_EVALUATORS
    RUN_EVALUATORS
    COMBINE_EVALUATIONS
} from "./modules.nf"

workflow {
    // Load files directly where needed instead of using shared channels
    all_no_sim_ch = Channel.fromPath("${params.combinedDockingResultsPath}/ALL_combined_results_no_chemical_similarity.csv")
    settings_file = Channel.fromPath("${params.configFiles}/settings_cross_docking_defaults.yml")

    name_ch = Channel.value("datesplit")

    CREATE_EVALUATORS(name_ch, all_no_sim_ch, settings_file)

    // Make sure to properly combine channels for the next process
    eval_inputs_ch = CREATE_EVALUATORS.out.evaluator_json
        .combine(name_ch)
        .combine(all_no_sim_ch)
        .map { json, name, data_file ->
            return [json, name, data_file]
        }

    RUN_EVALUATORS(eval_inputs_ch)

    COMBINE_EVALUATIONS(
        name_ch,
        RUN_EVALUATORS.out.evaluator_results.collect()
    )
}