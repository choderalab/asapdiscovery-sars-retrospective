#!/usr/bin/env nextflow
include {
    CREATE_EVALUATOR_FACTORY_SETTINGS
    CREATE_EVALUATORS_TWO
    RUN_EVALUATORS_TWO
    COMBINE_EVALUATIONS
} from "./modules.nf"

workflow RUN_DOCKING_ANALYSIS {
    take:
        name
        docking_results_parquet
        docking_results_json
        evaluator_settings

    main:
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
        )

        // Collect all evaluator results before combining
        all_results = RUN_EVALUATORS_TWO.output.evaluator_results
            .flatten()
            .collect()

        COMBINE_EVALUATIONS(
            name,
            all_results
        )
}

workflow DATESPLIT_POSIT {
    RUN_DOCKING_ANALYSIS('datesplit_posit', params.all_sim_parquet, params.all_sim_json, params.datesplit_settings)
}
workflow DATESPLIT_FRED {
    RUN_DOCKING_ANALYSIS('datesplit_fred', params.fred_sim_parquet, params.fred_sim_json, params.datesplit_settings)
}
workflow NOT_X_TO_X_POSIT {
    RUN_DOCKING_ANALYSIS('not_x_to_x_posit', params.all_sim_parquet, params.all_sim_json, params.not_x_to_x_scaffold_split)
}
workflow X_TO_NOT_X_POSIT {
    RUN_DOCKING_ANALYSIS('x_to_not_x_posit', params.all_sim_parquet, params.all_sim_json,  params.x_to_not_x_scaffold_split)
}
workflow X_TO_Y_POSIT {
    RUN_DOCKING_ANALYSIS('x_to_y_posit', params.all_sim_parquet, params.all_sim_json, params.x_to_y_default)
}
workflow X_TO_X_POSIT {
    RUN_DOCKING_ANALYSIS('x_to_x_posit', params.all_sim_parquet, params.all_sim_json, params.x_to_x_scaffold_split)
}
workflow INCREASING_SIMILARITY_TC_ALIGNED_POSIT{
    RUN_DOCKING_ANALYSIS('increasing_similarity_tanimoto_combo_aligned_posit', params.all_sim_parquet, params.all_sim_json, params.increasing_similarity_tanimoto_combo_aligned)
}
workflow INCREASING_SIMILARITY_TC_ALIGNED_FRED{
    RUN_DOCKING_ANALYSIS('increasing_similarity_tanimoto_combo_aligned_fred', params.fred_sim_parquet, params.fred_sim_json, params.increasing_similarity_tanimoto_combo_aligned)
}


workflow CREATE_EVALUATOR_FACTORY_SETTINGS_WORKFLOW {
    CREATE_EVALUATOR_FACTORY_SETTINGS()
}

workflow RUN_ANALYSIS {
    take:
        setup_analysis_check

    main:
        DATESPLIT_POSIT()
        DATESPLIT_FRED()
        NOT_X_TO_X_POSIT()
        X_TO_NOT_X_POSIT()
        X_TO_Y_POSIT()
        X_TO_X_POSIT()
        INCREASING_SIMILARITY_TC_ALIGNED_POSIT()
        INCREASING_SIMILARITY_TC_ALIGNED_FRED()
}

workflow {
    RUN_ANALYSIS(CREATE_EVALUATOR_FACTORY_SETTINGS_WORKFLOW().out.collect())

}