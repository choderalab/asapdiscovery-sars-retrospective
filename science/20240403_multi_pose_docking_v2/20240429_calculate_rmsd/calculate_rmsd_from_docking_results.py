# Description: Calculate RMSD between ligand poses

from pathlib import Path
from tqdm import tqdm
from asapdiscovery.docking.openeye import POSITDockingResults
from asapdiscovery.data.schema.ligand import Ligand
from asapdiscovery.data.readers.molfile import MolFileFactory
import argparse


def get_args():
    parser = argparse.ArgumentParser(description="Calculate RMSD between ligand poses")
    parser.add_argument(
        "-d",
        "--results_dir",
        type=Path,
        required=True,
        help="Path to directory containing docking results",
    )
    parser.add_argument(
        "-l",
        "--ligands",
        type=Path,
        required=True,
        help="Path to original ligand sdf file.",
    )
    parser.add_argument(
        "-o", "--output_file", type=str, required=True, help="Path to output file"
    )
    return parser.parse_args()


def calculate_ligand_rmsd(ref: Ligand, fit: Ligand):
    from asapdiscovery.data.backend.openeye import oechem

    fitmol = fit.to_oemol()
    refmol = ref.to_oemol()
    nConfs = fit.num_poses
    vecRmsd = oechem.OEDoubleArray(nConfs)
    success = oechem.OERMSD(refmol, fitmol, vecRmsd)
    if not success:
        print("RMSD calculation failed")
    fit.set_SD_data({"RMSD": list(vecRmsd)})
    return fit


def make_df_from_docking_results(results=list[POSITDockingResults]):
    import pandas as pd
    from asapdiscovery.docking.docking_data_validation import DockingResultCols

    dfs = []
    for result in results:
        docking_dict = {}
        docking_dict["Query_Ligand"] = result.input_pair.ligand.compound_name
        docking_dict["Reference_Structure"] = (
            result.input_pair.complex.target.target_name
        )
        docking_dict["Reference_Ligand_SMILES"] = (
            result.input_pair.complex.ligand.smiles
        )
        docking_dict[DockingResultCols.SMILES.value] = result.input_pair.ligand.smiles
        docking_dict[DockingResultCols.DOCKING_CONFIDENCE_POSIT.value] = (
            result.posed_ligand.conf_tags["docking-confidence-POSIT"]
        )
        docking_dict["RMSD"] = result.posed_ligand.conf_tags["RMSD"]
        docking_dict["Pose_ID"] = result.posed_ligand.conf_tags["Pose_ID"]
        docking_dict["POSIT_Method"] = result.posed_ligand.conf_tags["_POSIT_method"]
        docking_dict["Reference_Ligand"] = (
            result.input_pair.complex.ligand.compound_name
        )

        dfs.append(pd.DataFrame(docking_dict))

    df = pd.concat(dfs)
    return df


def main():
    args = get_args()
    results_dir = args.results_dir

    mff = MolFileFactory(filename=args.ligands)
    ligs = mff.load()
    lig_dict = {lig.compound_name: lig for lig in ligs}

    json_paths = list(results_dir.glob("docking_results/*/docking_result.json"))
    results = [
        POSITDockingResults.from_json_file(json_file) for json_file in json_paths
    ]

    for result in tqdm(results):
        posed_lig = result.posed_ligand
        ref = lig_dict[posed_lig.compound_name]
        calculate_ligand_rmsd(ref, posed_lig)

    df = make_df_from_docking_results(results)
    df.to_csv(args.output_file, index=False)


if __name__ == "__main__":
    main()
