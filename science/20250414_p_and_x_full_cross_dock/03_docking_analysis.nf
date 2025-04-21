#!/usr/bin/env nextflow
include {
    CALCULATE_RMSD
    COMBINE_AND_PROCESS_RESULTS
} from "./modules.nf"

workflow {
    // Define the list of methods
    def methods = ["ALL", "FRED"]

    // Create separate channels for each method
    all_docked_dirs = Channel
        .fromPath("${params.dockedFiles}/ALL/*docked", type: 'dir')
        .map { results_dir ->
            def id = results_dir.name.toString().find(/([a-zA-Z0-9_-]+)\_docked/) { match, code -> code }
            return tuple("ALL", id, results_dir)
        }

    fred_docked_dirs = Channel
        .fromPath("${params.dockedFiles}/FRED/*docked", type: 'dir')
        .map { results_dir ->
            def id = results_dir.name.toString().find(/([a-zA-Z0-9_-]+)\_docked/) { match, code -> code }
            return tuple("FRED", id, results_dir)
        }

    // Mix both channels
    docked_dirs = all_docked_dirs.mix(fred_docked_dirs)

    ligand_file_3d = Channel
        .fromPath("${params.ligandFiles}/${params.ligandFile3d}", type: 'file')

    // Combine each docked directory with the ligand file
    input_pairs = docked_dirs.combine(ligand_file_3d)

    // Run CALCULATE_RMSD for each pair
    CALCULATE_RMSD(input_pairs)

    // Collect the results into a single value
    input_csvs = CALCULATE_RMSD.out.rmsd_csv.collect()

    fixed_frag_cache = Channel
        .fromPath("${params.dataPath}/${params.fixedFragalysisCache}", type: 'dir')
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