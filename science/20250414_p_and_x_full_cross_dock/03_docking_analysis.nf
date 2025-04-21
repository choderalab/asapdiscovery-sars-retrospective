#!/usr/bin/env nextflow
include {
    CALCULATE_RMSD_ARRAY
    COMBINE_AND_PROCESS_RESULTS
} from "./modules.nf"

workflow {
    // Create channels from directories for docked directories and ligand_file_3d
    docked_dirs = Channel
        .fromPath("${params.dockedFiles}/*/*docked", type: 'dir')

    ligand_file_3d = Channel
        .fromPath("${params.ligandFiles}/${params.ligandFile3d}", type: 'file')

    // Combine each docked directory with the ligand file
    docked_dirs
        .combine(ligand_file_3d)
        .set { input_pairs }

    // Run CALCULATE_RMSD_ARRAY for each pair
    CALCULATE_RMSD_ARRAY(input_pairs)

    // combine the results into a single value
    input_csvs = CALCULATE_RMSD_ARRAY.out.rmsd_csv.collect()


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