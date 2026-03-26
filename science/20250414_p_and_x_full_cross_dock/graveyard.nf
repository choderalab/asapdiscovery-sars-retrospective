// Process to load and optionally flatten ligands
process LOAD_LIGANDS {
    tag "Loading ligands"

    input:
    path ligand_file

    output:
    path "processed_ligands.sdf", emit: ligands

    script:
    """
    #!/usr/bin/env python
    from asapdiscovery.data.readers.molfile import MolFileFactory

    # Load ligands
    molfile = MolFileFactory(filename="${ligand_file}")
    ligands = molfile.load()

    if ${params.flatten_ligands}:
        for mol in ligands:
            mol.flatten()

    # Write processed ligands
    with oemolostream("processed_ligands.sdf") as ofs:
        for mol in ligands:
            OEWriteMolecule(ofs, mol)
    """
}

// Process to load protein structures
process LOAD_STRUCTURES {
    tag "Loading structures"
    publishDir "${params.output_dir}/intermediate/structures", mode: 'copy'

    input:
    path structure_dir
    path fragalysis_dir

    output:
    path "structures.pkl", emit: structures

    script:
    """
    #!/usr/bin/env python
    import pickle
    from asapdiscovery.data.readers.meta_structure_factory import MetaStructureFactory

    factory = MetaStructureFactory(
        structure_dir="${structure_dir}",
        fragalysis_dir="${fragalysis_dir}"
    )
    complexes = factory.load()

    with open("structures.pkl", "wb") as f:
        pickle.dump(complexes, f)
    """
}

// Process to create docking pairs
process CREATE_PAIRS {
    tag "Creating pairs"
    publishDir "${params.output_dir}/intermediate/pairs", mode: 'copy'

    input:
    path ligands
    path structures

    output:
    path "docking_pairs.pkl", emit: pairs

    script:
    """
    #!/usr/bin/env python
    import pickle
    from asapdiscovery.data.readers.molfile import MolFileFactory
    from asapdiscovery.docking.selectors.selector_list import StructureSelector

    # Load ligands and structures
    molfile = MolFileFactory(filename="${ligands}")
    query_ligands = molfile.load()

    with open("${structures}", "rb") as f:
        structures = pickle.load(f)

    # Create pairs
    selector = StructureSelector.${params.selector}.selector_cls()
    pairs = selector.select(query_ligands, structures)

    with open("docking_pairs.pkl", "wb") as f:
        pickle.dump(pairs, f)
    """
}

// Process to run POSIT docking
process RUN_DOCKING {
    tag "Running POSIT docking"
    publishDir "${params.output_dir}/intermediate/docking", mode: 'copy'

    input:
    path pairs

    output:
    path "docking_results.pkl", emit: results

    script:
    """
    #!/usr/bin/env python
    import pickle
    from asapdiscovery.docking.openeye import POSITDocker

    with open("${pairs}", "rb") as f:
        pairs = pickle.load(f)

    docker = POSITDocker(
        posit_method="${params.posit_method}",
        use_omega=${params.use_omega},
        omega_dense=${params.omega_dense},
        num_poses=${params.num_poses},
        allow_retries=${params.allow_retries},
        allow_final_clash=${params.allow_final_clash},
        relax_mode="${params.relax_mode}"
    )

    results = docker.dock(pairs)

    with open("docking_results.pkl", "wb") as f:
        pickle.dump(results, f)
    """
}

// Process to score and format results
process SCORE_AND_FORMAT {
    tag "Scoring and formatting results"
    publishDir "${params.output_dir}/final", mode: 'copy'

    input:
    path docking_results

    output:
    path "final_poses.sdf", emit: sdf
    path "results.csv", emit: csv

    script:
    """
    #!/usr/bin/env python
    import pickle
    import pandas as pd
    from asapdiscovery.docking.scorer import ChemGauss4Scorer, MetaScorer
    from asapdiscovery.docking.docking import write_results_to_multi_sdf

    # Load results
    with open("${docking_results}", "rb") as f:
        results = pickle.load(f)

    # Score results
    scorer = MetaScorer(scorers=[ChemGauss4Scorer()])
    scores_df = scorer.score(results, return_df=True)

    # Write poses to SDF
    write_results_to_multi_sdf("final_poses.sdf", results)

    # Add RMSD calculation placeholder
    if ${params.calculate_rmsd}:
        # TODO: Add RMSD calculation code here
        pass

    # Save results
    scores_df.to_csv("results.csv", index=False)
    """
}

workflow {
    // Load input data
    ligands_ch = Channel.fromPath(params.ligands)
    structure_dir_ch = Channel.fromPath(params.structure_dir)
    fragalysis_dir_ch = Channel.fromPath(params.fragalysis_dir)

    // Run workflow
    LOAD_LIGANDS(ligands_ch)
    LOAD_STRUCTURES(structure_dir_ch, fragalysis_dir_ch)
    CREATE_PAIRS(LOAD_LIGANDS.out.ligands, LOAD_STRUCTURES.out.structures)
    RUN_DOCKING(CREATE_PAIRS.out.pairs)
    SCORE_AND_FORMAT(RUN_DOCKING.out.results)
}