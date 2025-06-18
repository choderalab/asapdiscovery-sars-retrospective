#!/usr/bin/env nextflow
include {
    CREATE_EVALUATOR_FACTORY_SETTINGS
    CREATE_EVALUATORS
    RUN_EVALUATORS
    COMBINE_EVALUATIONS
} from "./modules.nf"
params.K = 10

workflow RUN_DOCKING_ANALYSIS {
    take:
        name
        docking_results_parquet
        docking_results_json
        evaluator_settings

    main:
        CREATE_EVALUATORS(
            name,
            evaluator_settings,
            docking_results_parquet,
            docking_results_json
        )

        // Create channel from JSON files only after evaluator creation
        eval_inputs_ch = CREATE_EVALUATORS.output.evaluator_json_directory
            .flatMap { dir -> file("${dir}/*.json") }
            .buffer(size: params.K)

        RUN_EVALUATORS(
            name,
            docking_results_parquet,
            docking_results_json,
            eval_inputs_ch,
        )

        // Collect all evaluator results before combining
        all_results = RUN_EVALUATORS.output.evaluator_results
            .flatten()
            .collect()

        COMBINE_EVALUATIONS(
            name,
            all_results
        )
}
dataset_names = [
"posit_single_pose": "ALL_1_poses",
// "fred_single_pose": "FRED_1_poses",
]

def results = [:]
dataset_names.each { label, name ->
    def parquet = "${params.dataPath}/${name}.parquet"
    def json = "${params.dataPath}/${name}.json"

    results[label] = [  // Store directly in map with label as key
        name: name,
        docking_results_parquet: parquet,
        docking_results_json: json
    ]
}

// Print dataset definitions
println "\nDataset Definitions:"
println "===================="
results.each { label, data ->
    println """
    Name: ${label}
    Label: ${data.name}
    Parquet: ${data.docking_results_parquet}
    JSON: ${data.docking_results_json}
    -------------------"""
}

settings_map = [
"datesplit": "reference_split_comparison.yaml",
"x_to_x": "x_to_x_scaffold_split.yaml",
"x_to_x_5": "x_to_x_scaffold_split_5_refs.yaml",
"x_to_y": "x_to_y_scaffold_split.yaml",
"x_to_y_5": "x_to_y_scaffold_split_5_refs.yaml",
"ecfp4": "increasing_similarity_ecfp4.yaml",
"mcs": "increasing_similarity_mcs.yaml",
"tc": "increasing_similarity_tanimoto_combo_aligned.yaml",]

def settings = [:]
settings_map.each { label, filename ->
    settings[label] = [name: name, filename: "${params.evaluator_configs}/${filename}"]
}

workflow {
        RUN_DOCKING_ANALYSIS(
            "${results.posit_single_pose.name}_${settings.datesplit.name}",
            results.posit_single_pose.docking_results_parquet,
            results.posit_single_pose.docking_results_json,
            settings.datesplit.filename
        )
}



// workflow DATESPLIT_POSIT {
//     RUN_DOCKING_ANALYSIS(params.all_sim_parquet, params.all_sim_json, params.datesplit_settings)
// }
// workflow DATESPLIT_FRED {
//     RUN_DOCKING_ANALYSIS('datesplit_fred', params.fred_sim_parquet, params.fred_sim_json, params.datesplit_settings)
// }
// workflow X_TO_X_POSIT {
//     RUN_DOCKING_ANALYSIS('x_to_x_posit', params.all_sim_parquet, params.all_sim_json, params.x_to_x_scaffold_split)
// }
// workflow X_TO_X_POSIT_5_REFS {
//     RUN_DOCKING_ANALYSIS('x_to_x_posit_5_refs', params.all_sim_parquet, params.all_sim_json, params.x_to_x_scaffold_split_5_refs)
// }
// workflow X_TO_Y_POSIT {
//     RUN_DOCKING_ANALYSIS('x_to_y_posit', params.all_sim_parquet, params.all_sim_json, params.x_to_y_scaffold_split)
// }
// workflow X_TO_Y_POSIT_5_REFS {
//     RUN_DOCKING_ANALYSIS('x_to_y_posit_5_refs', params.all_sim_parquet, params.all_sim_json, params.x_to_y_scaffold_split_5_refs)
// }
// workflow NOT_X_TO_X_POSIT {
//     RUN_DOCKING_ANALYSIS('not_x_to_x_posit', params.all_sim_parquet, params.all_sim_json, params.not_x_to_x_scaffold_split)
// }
// workflow NOT_X_TO_X_POSIT_5_REFS {
//     RUN_DOCKING_ANALYSIS('not_x_to_x_posit_5_refs', params.all_sim_parquet, params.all_sim_json, params.not_x_to_x_scaffold_split_5_refs)
// }
// workflow X_TO_NOT_X_POSIT {
//     RUN_DOCKING_ANALYSIS('x_to_not_x_posit', params.all_sim_parquet, params.all_sim_json,  params.x_to_not_x_scaffold_split)
// }
// workflow INCREASING_SIMILARITY_TC_ALIGNED_POSIT{
//     RUN_DOCKING_ANALYSIS('increasing_similarity_tanimoto_combo_aligned_posit', params.all_sim_parquet, params.all_sim_json, params.increasing_similarity_tanimoto_combo_aligned)
// }
// workflow INCREASING_SIMILARITY_TC_ALIGNED_FRED{
//     RUN_DOCKING_ANALYSIS('increasing_similarity_tanimoto_combo_aligned_fred', params.fred_sim_parquet, params.fred_sim_json, params.increasing_similarity_tanimoto_combo_aligned)
// }
// workflow INCREASING_SIMILARITY_MCS_POSIT{
//     RUN_DOCKING_ANALYSIS('increasing_similarity_mcs_posit', params.all_sim_parquet, params.all_sim_json, params.increasing_similarity_mcs)
// }
// workflow INCREASING_SIMILARITY_MCS_FRED{
//     RUN_DOCKING_ANALYSIS('increasing_similarity_mcs_fred', params.fred_sim_parquet, params.fred_sim_json, params.increasing_similarity_mcs)
// }
// workflow INCREASING_SIMILARITY_ECFP4_POSIT{
//     RUN_DOCKING_ANALYSIS('increasing_similarity_ecfp4_posit', params.all_sim_parquet, params.all_sim_json, params.increasing_similarity_ecfp4)
// }
// workflow INCREASING_SIMILARITY_ECFP4_FRED{
//     RUN_DOCKING_ANALYSIS('increasing_similarity_ecfp4_fred', params.fred_sim_parquet, params.fred_sim_json, params.increasing_similarity_ecfp4)
// }
// workflow CREATE_EVALUATOR_FACTORY_SETTINGS_WORKFLOW {
//     CREATE_EVALUATOR_FACTORY_SETTINGS()
// }
//
// workflow INCREASING_SIMILARITY_ECFP4_POSIT_MULTIPOSE {
//     RUN_DOCKING_ANALYSIS('increasing_similarity_ecfp4_posit_multipose', params.all_multipose_parquet, params.all_multipose_json, params.increasing_similarity_ecfp4)
// }
//
// workflow RUN_DATESPLIT {
//     DATESPLIT_POSIT()
//     DATESPLIT_FRED()
// }
// workflow RUN_SCAFFOLD_SPLIT {
//     X_TO_X_POSIT()
//     X_TO_X_POSIT_5_REFS()
//
//     X_TO_Y_POSIT()
//     X_TO_Y_POSIT_5_REFS()
//
//     X_TO_NOT_X_POSIT()
//
//     NOT_X_TO_X_POSIT()
//     NOT_X_TO_X_POSIT_5_REFS()
// }
// workflow RUN_SIMILARITY_SPLIT {
//     INCREASING_SIMILARITY_TC_ALIGNED_POSIT()
//         INCREASING_SIMILARITY_TC_ALIGNED_FRED()
//         INCREASING_SIMILARITY_MCS_POSIT()
//         INCREASING_SIMILARITY_MCS_FRED()
//         INCREASING_SIMILARITY_ECFP4_POSIT()
//         INCREASING_SIMILARITY_ECFP4_FRED()
// }
//
// workflow RUN_ANALYSIS {
//     take:
//         setup_analysis_check
//
//     main:
//         RUN_DATESPLIT()
//         RUN_SCAFFOLD_SPLIT()
//         RUN_SIMILARITY_SPLIT()
// }
//
// workflow {
//     RUN_ANALYSIS(CREATE_EVALUATOR_FACTORY_SETTINGS_WORKFLOW().out.collect())
//
// }