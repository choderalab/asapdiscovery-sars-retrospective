#!/usr/bin/env nextflow
include {
    CREATE_EVALUATORS
    RUN_EVALUATORS
    COMBINE_EVALUATIONS
} from "./modules.nf"

workflow RUN_DOCKING_ANALYSIS {
    take:
    name
    docking_results
    settings

    main:
    CREATE_EVALUATORS(name, docking_results, settings)

    CREATE_EVALUATORS.out.evaluator_json
        .flatten()
        .buffer(size: params.K)
        .set { eval_inputs_ch }

    RUN_EVALUATORS(name, docking_results, eval_inputs_ch)

    COMBINE_EVALUATIONS(
        name,
        RUN_EVALUATORS.out.evaluator_results.collect()
    )

    emit:
    results = COMBINE_EVALUATIONS.out
}
workflow DATESPLIT_POSIT {
    RUN_DOCKING_ANALYSIS('datesplit_posit', params.all_no_sim, params.datesplit_settings)
}
workflow DATESPLIT_FRED {
    RUN_DOCKING_ANALYSIS('datesplit_fred', params.fred_no_sim, params.datesplit_settings)
}
workflow MULTIPOSE_POSIT {
    RUN_DOCKING_ANALYSIS('multipose_posit', params.all_no_sim, params.multipose_settings)
}
workflow MULTIPOSE_FRED {
    RUN_DOCKING_ANALYSIS('multipose_fred', params.fred_no_sim, params.multipose_settings)
}
workflow NOT_X_TO_X_POSIT {
    RUN_DOCKING_ANALYSIS('not_x_to_x_posit', params.all_sim, params.settings_scaffold_split_not_x_to_x)
}
workflow X_TO_NOT_X_POSIT {
    RUN_DOCKING_ANALYSIS('x_to_not_x_posit', params.all_sim, params.settings_scaffold_split_x_to_not_x)
}
workflow X_TO_Y_POSIT {
    RUN_DOCKING_ANALYSIS('x_to_y_posit', params.all_sim, params.settings_scaffold_split_x_to_y)
}

// Main workflow to run all analyses in parallel
workflow {
    DATESPLIT_POSIT()
    DATESPLIT_FRED()
    NOT_X_TO_X_POSIT()
    X_TO_NOT_X_POSIT()
    X_TO_Y_POSIT()

}