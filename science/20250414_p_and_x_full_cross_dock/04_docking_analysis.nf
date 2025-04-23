#!/usr/bin/env nextflow
include {
    CREATE_EVALUATORS
    RUN_EVALUATORS
    COMBINE_EVALUATIONS
} from "./modules.nf"

params.K = 1

workflow {
    // Load files directly where needed instead of using shared channels
    all_no_sim_ch = Channel.fromPath("${params.combinedDockingResultsPath}/ALL_combined_results_no_chemical_similarity.csv", type: 'file')
    settings_file = Channel.fromPath("${params.configFiles}/settings_cross_docking_defaults.yml", type: 'file')

    name_ch = Channel.value("datesplit")

    CREATE_EVALUATORS(name_ch, all_no_sim_ch, settings_file)

    // map the number at the end of the file name as an id
    CREATE_EVALUATORS.out.evaluator_json
        .flatten()
        .buffer(size: params.K)
        .set { eval_inputs_ch }
    }
//         .map { file ->
//         def id = file.name.toString().find(/([0-9]+)/) { match, code -> code }
//         return tuple(id, file)

    eval_inputs_ch
        .combine(name_ch)
        .combine(all_no_sim_ch)
        .set { eval_inputs_ch }

    RUN_EVALUATORS(eval_inputs_ch)

    COMBINE_EVALUATIONS(
        name_ch,
        RUN_EVALUATORS.out.evaluator_results.collect()
    )
}