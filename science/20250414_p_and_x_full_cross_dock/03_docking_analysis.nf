#!/usr/bin/env nextflow
include {
    CALCULATE_RMSD
    COMBINE_AND_PROCESS_RESULTS
} from "./modules.nf"

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

    COMBINE_AND_PROCESS_RESULTS(
        input_csvs,
        fixed_frag_cache,
        chemical_similarity_data,
        date_dict,
        chemical_scaffold_data,
        method,
    )
}
// Create named entry points for each dataset
workflow PROCESS_FRED {
    COMBINE_DOCKING_RESULTS('FRED')
}

workflow PROCESS_ALL {
    COMBINE_DOCKING_RESULTS('ALL')
}

workflow {
    PROCESS_FRED()
    PROCESS_ALL()
}


// workflow {
//     // Define the list of methods
//     def methods = ["ALL", "FRED"]
//
//     // Create separate channels for each method
//     all_docked_dirs = Channel
//         .fromPath("${params.dockedFiles}/ALL/*docked", type: 'dir')
//         .map { results_dir ->
//             def id = results_dir.name.toString().find(/([a-zA-Z0-9_-]+)\_docked/) { match, code -> code }
//             return tuple("ALL", id, results_dir)
//         }
//
//     fred_docked_dirs = Channel
//         .fromPath("${params.dockedFiles}/FRED/*docked", type: 'dir')
//         .map { results_dir ->
//             def id = results_dir.name.toString().find(/([a-zA-Z0-9_-]+)\_docked/) { match, code -> code }
//             return tuple("FRED", id, results_dir)
//         }
//
//     // Mix both channels
//     docked_dirs = all_docked_dirs.mix(fred_docked_dirs)
//
//     ligand_file_3d = Channel
//         .fromPath("${params.ligandFiles}/${params.ligandFile3d}", type: 'file')
//
//     // Combine each docked directory with the ligand file
//     input_pairs = docked_dirs.combine(ligand_file_3d)
//
//     // Run CALCULATE_RMSD for each pair
//     CALCULATE_RMSD(input_pairs)
//
//     // Collect the results into a single value
//     input_csvs = CALCULATE_RMSD.out.rmsd_csv.collect()
//
//     fixed_frag_cache = Channel
//         .fromPath("${params.fixedFragalysisCachePath}", type: 'dir')
//     chemical_similarity_data = Channel
//         .fromPath("${params.combinedChemicalSimilarityPath}", type: 'dir')
//     date_dict = Channel
//         .fromPath("${params.dateDictPath}", type: 'file')
//     chemical_scaffold_data = Channel
//         .fromPath("${params.genericScaffoldPath}", type: 'file')
//
//     COMBINE_AND_PROCESS_RESULTS(
//         input_csvs,
//         fixed_frag_cache,
//         chemical_similarity_data,
//         date_dict,
//         chemical_scaffold_data
//     )
// }