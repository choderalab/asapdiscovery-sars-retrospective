"""
Script to calculate the Maximum Common Substructure between reference and query ligands.
"""

from openeye import oechem
from asapdiscovery.data.readers.molfile import MolFileFactory
import pandas as pd
import argparse
from pathlib import Path
from asapdiscovery.data.util.logging import FileLogger
import numpy as np


def parse_args():
    parser = argparse.ArgumentParser(
        description="Calculate ECFP fingerprint similarities between ligands"
    )
    parser.add_argument(
        "--ref-ligand-sdf",
        type=Path,
        required=True,
        help="Path to directory containing prepped reference ligand sdf.",
    )
    parser.add_argument(
        "--output-dir", required=True, type=Path, help="Path to output directory"
    )
    parser.add_argument(
        "--query-ligand-sdf",
        type=Path,
        required=False,
        help="Path to directory containing prepped query ligand sdf. If false, ref-ligand-sdf will be used.",
    )
    return parser.parse_args()


def one_to_many_mcs(refmol: oechem.OEMol, querymols: list[oechem.OEMol]):
    """
    Get the number of atoms in the maximum common substructure between each pair of molecules.
    :param mols:
    :return:
    """

    # these are the defaaults for atom and bond expressions but just to be explicit I'm putting them here
    atomexpr = (
        oechem.OEExprOpts_Aromaticity
        | oechem.OEExprOpts_AtomicNumber
        | oechem.OEExprOpts_FormalCharge
    )
    bondexpr = oechem.OEExprOpts_Aromaticity | oechem.OEExprOpts_BondOrder

    # Set up the search pattern and MCS objects
    mcs_num_atoms = np.zeros((len(querymols)), dtype=int)
    total_num_atoms = np.array([refmol.NumAtoms()] * len(querymols), dtype=int)
    pattern_query = oechem.OEQMol(refmol)
    pattern_query.BuildExpressions(atomexpr, bondexpr)
    mcss = oechem.OEMCSSearch(pattern_query)
    mcss.SetMCSFunc(oechem.OEMCSMaxAtomsCompleteCycles())

    for j, querymol in enumerate(querymols):
        # MCS search
        try:
            mcs = next(iter(mcss.Match(querymol, True)))
            mcs_num_atoms[j] = mcs.NumAtoms()
        except StopIteration:  # no match found
            mcs_num_atoms[j] = 0
        total_num_atoms[j] += querymol.NumAtoms()
    return mcs_num_atoms, total_num_atoms


def main():
    args = parse_args()
    output_dir = args.output_dir
    output_dir.mkdir(exist_ok=True, parents=True)

    logger = FileLogger(
        "calculate_mcs_tanimoto",
        output_dir,
        logfile="calculate_mcs_tanimoto.log",
    ).getLogger()

    logger.info("Loading molecules...")
    references = MolFileFactory(filename=args.ref_ligand_sdf).load()
    queries = (
        MolFileFactory(filename=args.query_ligand_sdf).load()
        if args.query_ligand_sdf
        else references.copy()
    )
    query_mols = [query.to_oemol() for query in queries]
    query_names = [query.compound_name for query in queries]

    logger.info("Calculating similarities...")
    dfs = []
    for ref in references:
        refmol = ref.to_oemol()
        mcs_num_atoms, total_num_atoms = one_to_many_mcs(refmol, query_mols)
        tanimoto = mcs_num_atoms / total_num_atoms
        df = pd.DataFrame(
            {
                "Reference_Ligand": ref.compound_name,
                "Query_Ligand": query_names,
                "MCS_Num_Atoms": mcs_num_atoms,
                "Total_Num_Atoms": total_num_atoms,
                "Tanimoto": tanimoto,
            }
        )
        dfs.append(df)

    # Save results
    logger.info("Saving results...")
    df = pd.concat(dfs, ignore_index=True)
    output_path = output_dir / "mcs_tanimoto.csv"
    df.to_csv(output_path, index=False)
    logger.info(f"Results saved to {output_path}")


if __name__ == "__main__":
    main()
