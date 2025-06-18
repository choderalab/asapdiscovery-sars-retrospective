#!/usr/bin/env nextflow
include {
    CALCULATE_RMSD
    COMBINE_AND_PROCESS_RESULTS
    CONVERT_TO_DOCKING_DATA_MODEL
} from "./modules.nf"

workflow COMBINE_DOCKING_RESULTS {
    take:
        name

    main:
        docked_dirs = Channel
            .fromPath("${params.dockedFiles}/${name}/*docked", type: 'dir')
            .map { results_dir ->
                def id = results_dir.name.toString().find(/([a-zA-Z0-9_-]+)\_docked/) { match, code -> code }
                return tuple(name, id, results_dir)
            }
        ligand_file_3d = Channel
            .fromPath("${params.ligandFiles}/${params.ligandFile3d}", type: 'file')

        // Combine each docked directory with the ligand file
        input_pairs = docked_dirs.combine(ligand_file_3d)

        // Run CALCULATE_RMSD for each pair
        CALCULATE_RMSD(input_pairs)

        // Collect the results into a single value
        input_csvs = CALCULATE_RMSD.out.rmsd_csv.collect()

        // Convert method to a channel
        name_ch = Channel.value(name)

        COMBINE_AND_PROCESS_RESULTS(
            input_csvs,
            name_ch
        )
}

// Create named entry points for each dataset
workflow PROCESS_FRED {
    COMBINE_DOCKING_RESULTS('FRED_1_poses')
}

workflow PROCESS_ALL {
    COMBINE_DOCKING_RESULTS('ALL_50_poses')
}
workflow PROCESS_ALL_SINGLE_POSE {
    COMBINE_DOCKING_RESULTS('ALL_1_poses')
}

workflow {
    PROCESS_FRED()
    PROCESS_ALL()
}