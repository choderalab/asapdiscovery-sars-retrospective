#!/usr/bin/env nextflow
include {
    CALCULATE_RMSDs
    COMBINE_AND_PROCESS_RESULTS
} from "./modules.nf"

workflow {
    docking_methods = Channel.from('ALL', 'FRED')

    // Define the list of values you want to iterate through
    def methods = ["ALL", "FRED"]

    // Create a channel from the list
    Channel
        .fromList(methods)
        .map { method ->
            // For each method, create a tuple of (method, dir)
            def results_dir = file("${params.dockedFiles}/${method}/*docked", type: 'dir')
            def id = results_dir.name.toString().find(/([a-zA-Z0-9_-]+)\_docked/) { match, code -> code }
            return tuple(method, id, results_dir)
        }
        .set { docked_dirs }

    ligand_file_3d = Channel
        .fromPath("${params.ligandFiles}/${params.ligandFile3d}", type: 'file')

    // Combine each docked directory with the ligand file
    docked_dirs
        .combine(ligand_file_3d)
        .set { input_pairs }

    // Run CALCULATE_RMSD_ARRAY for each pair
    CALCULATE_RMSDs(input_pairs)

    // combine the results into a single value
    input_csvs = CALCULATE_RMSDs.out.rmsd_csv.collect()


    // load files from channels
    fixed_frag_cache = Channel
        .fromPath("${params.dataPath}/${params.fixedFragalysisCache}/*", type: 'dir')
    chemical_similarity_data = Channel
        .fromPath("${params.chemicalSimilarityData}", type: 'dir')
    date_dict = Channel
        .fromPath("${params.dataPath}/cmpd_date_dict/date_dict.json", type: 'file')
    chemical_scaffold_data = Channel
        .fromPath("${params.dataPath}/cmpd_scaffold_dict/chemical_scaffold_data.json", type: 'file')
    COMBINE_AND_PROCESS_RESULTS(
        input_csvs,
        fixed_frag_cache,
        chemical_similarity_data,
        date_dict,
        chemical_scaffold_data
    )
}