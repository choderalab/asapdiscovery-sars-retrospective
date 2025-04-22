#!/usr/bin/env nextflow
include {
    CALCULATE_RMSD
    COMBINE_AND_PROCESS_RESULTS
} from "./modules.nf"

// Define shared channels for passing data between workflows
Channel.empty().set { combined_results_FRED }
Channel.empty().set { combined_results_no_similarity_FRED }
Channel.empty().set { combined_results_ALL }
Channel.empty().set { combined_results_no_similarity_ALL }

workflow COMBINE_DOCKING_RESULTS {
    take:
    method

    main:
    docked_dirs = Channel
        .fromPath("${params.dockedFiles}/${method}/*docked", type: 'dir')
        .map { results_dir ->
            def id = results_dir.name.toString().find(/([a-zA-Z0-9_-]+)\_docked/) { match, code -> code }
            return tuple(method, id, results_dir)
        }
    ligand_file_3d = Channel
        .fromPath("${params.ligandFiles}/${params.ligandFile3d}", type: 'file')

    // Combine each docked directory with the ligand file
    input_pairs = docked_dirs.combine(ligand_file_3d)

    // Run CALCULATE_RMSD for each pair
    CALCULATE_RMSD(input_pairs)

    // Collect the results into a single value
    input_csvs = CALCULATE_RMSD.out.rmsd_csv.collect()

    fixed_frag_cache = Channel
        .fromPath("${params.fixedFragalysisCachePath}", type: 'dir')
    chemical_similarity_data = Channel
        .fromPath("${params.combinedChemicalSimilarityPath}", type: 'dir')
    date_dict = Channel
        .fromPath("${params.dateDictPath}", type: 'file')
    chemical_scaffold_data = Channel
        .fromPath("${params.genericScaffoldPath}", type: 'file')

    // Convert method to a channel
    method_ch = Channel.value(method)

    COMBINE_AND_PROCESS_RESULTS(
        input_csvs,
        fixed_frag_cache,
        chemical_similarity_data,
        date_dict,
        chemical_scaffold_data,
        method_ch
    )

    emit:
    combined_results = COMBINE_AND_PROCESS_RESULTS.out.combined_results_with_similarity
    combined_results_no_similarity = COMBINE_AND_PROCESS_RESULTS.out.combined_results_no_similarity
}

// Create named entry points for each dataset
workflow PROCESS_FRED {
    COMBINE_DOCKING_RESULTS('FRED')

    // Publish to shared channel
    COMBINE_DOCKING_RESULTS.out.combined_results.tap { combined_results_FRED }
    COMBINE_DOCKING_RESULTS.out.combined_results_no_similarity.tap { combined_results_no_similarity_FRED }
}

workflow PROCESS_ALL {
    COMBINE_DOCKING_RESULTS('ALL')

    // Publish to shared channel
    COMBINE_DOCKING_RESULTS.out.combined_results.tap { combined_results_ALL }
    COMBINE_DOCKING_RESULTS.out.combined_results_no_similarity.tap { combined_results_no_similarity_ALL }
}

workflow PROCESS_RESULTS {
    PROCESS_FRED()
    PROCESS_ALL()
}

// Define analysis workflow
include {
    CREATE_EVALUATORS
    RUN_EVALUATORS
    COMBINE_EVALUATIONS
} from "./modules.nf"

workflow DATASETSPLIT_ANALYSIS {
    // Use the shared channel
    CREATE_EVALUATORS("datesplit", combined_results_no_similarity_ALL)

    // Create a channel with "datesplit" value for combination
    datesplit_ch = Channel.value("datesplit")

    // Combine channels in the correct order for the process
    eval_inputs_ch = CREATE_EVALUATORS.out.evaluator_json
        .combine(datesplit_ch)
        .combine(combined_results_no_similarity_ALL)
        .map { json, split_type, results_path ->
            // Reorder to match process input requirements
            return [split_type, results_path, json]
        }

    RUN_EVALUATORS(eval_inputs_ch)

    COMBINE_EVALUATIONS(
        Channel.value("datesplit"),
        RUN_EVALUATORS.out.evaluator_results
    )
}

workflow RUN_ANALYSIS {
    DATASETSPLIT_ANALYSIS()
}

workflow {
    // Run both workflows in sequence
    // PROCESS_RESULTS will populate the shared channels
    // Then RUN_ANALYSIS will use those channels
    PROCESS_RESULTS()
    RUN_ANALYSIS()
}