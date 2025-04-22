#!/usr/bin/env nextflow
include {
    CREATE_EVALUATORS
    RUN_EVALUATORS
    COMBINE_EVALUATIONS
} from "./modules.nf"

workflow {
    // Load files directly where needed instead of using shared channels
    all_no_sim_ch = Channel.fromPath("${params.combinedDockingResultsPath}/ALL_combined_results_no_chemical_similarity.csv").collect()
    settings_file = Channel.fromPath("${params.configFiles}/settings_cross_docking_defaults.yml").collect()

    name_ch = Channel.value("datesplit")

    CREATE_EVALUATORS(name_ch, all_no_sim_ch, settings_file)

    // map the number at the end of the file name as an id
    eval_inputs_ch = CREATE_EVALUATORS.out.evaluator_json
        .flatten()
        .map { file ->
        def id = file.name.toString().find(/([0-9]+)\_.json/) { match, code -> code }
        return tuple(id, file, name_ch, all_no_sim_ch)
    }

    // view first eval_inputs_ch
    eval_inputs_ch
        .first()
        .view{tuple -> "First eval_inputs_ch: $tuple"}



    RUN_EVALUATORS(eval_inputs_ch)

    COMBINE_EVALUATIONS(
        name_ch,
        RUN_EVALUATORS.out.evaluator_results.collect()
    )
}