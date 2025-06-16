#!/usr/bin/env nextflow
include {
    CREATE_EVALUATOR_FACTORY_SETTINGS
    CREATE_EVALUATORS
    RUN_EVALUATORS
    COMBINE_EVALUATIONS
} from "./modules.nf"
params.K = 10
params.analysis_config = "docking_analysis_config.yaml"

// Load configuration
def config = readYamlConfig(params.analysis_config)

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

// Helper function to generate workflow names
def getWorkflowName(analysis, dataset, variant = null) {
    def parts = [analysis, dataset]
    if (variant) parts.add(variant)
    return parts.join('_')
}

// Generate workflows dynamically based on config
config.analyses.each { analysis_name, analysis_config ->
    analysis_config.each { variant_name, variant_config ->
        variant_config.enabled_datasets.each { dataset_name ->
            def dataset = config.datasets[dataset_name]
            def workflow_name = getWorkflowName(analysis_name, dataset_name, variant_name)
            def dataset_parquet = "${params.combinedDockingResultsPath}/${dataset_name}.parquet"
            def dataset_json = "${params.combinedDockingResultsPath}/${dataset_name}.json"

            workflow."${workflow_name}" = {
                RUN_DOCKING_ANALYSIS(
                    workflow_name,
                    dataset_parquet,
                    dataset_json,
                    variant_config.settings
                )
            }
        }
    }
}

workflow RUN_ANALYSIS {
    take:
        setup_analysis_check

    main:
        // Dynamically call all enabled workflows
        config.analyses.each { analysis_name, analysis_config ->
                analysis_config.variants.each { variant_name, variant_config ->
                    variant_config.enabled_datasets.each { dataset_name ->
                        workflow."${getWorkflowName(analysis_name, dataset_name, variant_name)}"()
                    }
                }
        }
}

workflow {
    RUN_ANALYSIS(CREATE_EVALUATOR_FACTORY_SETTINGS_WORKFLOW().out.collect())
}