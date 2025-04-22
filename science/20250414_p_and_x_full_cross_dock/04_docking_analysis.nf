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

    // Debug - print the file paths to ensure they exist
    all_no_sim_ch.view { "Found ALL_no_sim file: $it" }
    settings_file.view { "Found settings file: $it" }

    // Fixed input format - check if CREATE_EVALUATORS expects a tuple or separate inputs
    name_ch = Channel.value("datesplit")

    // If CREATE_EVALUATORS expects separate parameters:
    CREATE_EVALUATORS(name_ch, all_no_sim_ch, settings_file)

    // Debug - check if evaluator_json is being created
    CREATE_EVALUATORS.out.evaluator_json.view { "Created evaluator JSON: $it" }

    // Make sure to properly combine channels for the next process
    eval_inputs_ch = CREATE_EVALUATORS.out.evaluator_json
        .combine(name_ch)
        .combine(all_no_sim_ch)
        .map { json, name, data_file ->
            return [name, data_file, json]  // Adjust order as needed for your process
        }

    RUN_EVALUATORS(eval_inputs_ch)

    COMBINE_EVALUATIONS(
        name_ch,
        RUN_EVALUATORS.out.evaluator_results.collect()
    )
}