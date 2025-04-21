#!/usr/bin/env nextflow
include {
    CALCULATE_RMSD
    COMBINE_AND_PROCESS_RESULTS
} from "./modules.nf"

workflow {
    // Define the list of methods
    def methods = ["ALL", "FRED"]

    // Create a channel for the methods
    Channel
        .fromList(methods)
        .flatMap { method ->
            // Use fromPath to get all matching directories
            Channel.fromPath("${params.dockedFiles}/${method}/*docked", type: 'dir')
                .map { results_dir ->
                    def id = results_dir.name.toString().find(/([a-zA-Z0-9_-]+)\_docked/) { match, code -> code }
                    return tuple(method, id, results_dir)
                }
        }
        .set { docked_dirs }

    ligand_file_3d = Channel
        .fromPath("${params.ligandFiles}/${params.ligandFile3d}", type: 'file')

    // Combine each docked directory with the ligand file
    docked_dirs
        .combine(ligand_file_3d)
        .set { input_pairs }

    // Run CALCULATE_RMSD_ARRAY for each pair
    CALCULATE_RMSD(input_pairs)

    // combine the results into a single value
    input_csvs = CALCULATE_RMSD.out.rmsd_csv.collect()

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