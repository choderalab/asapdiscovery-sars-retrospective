# Description: Calculate RMSD between ligand poses

from pathlib import Path
from tqdm import tqdm
from asapdiscovery.docking.openeye import POSITDockingResults
from asapdiscovery.data.schema.ligand import Ligand
from asapdiscovery.data.readers.molfile import MolFileFactory
from asapdiscovery.data.backend.openeye import oechem
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
    parser.add_argument(
        "--cutoff", type=float, default=2.0, help="RMSD cutoff for distinct poses."
    )
    return parser.parse_args()


def calculate_ligand_rmsd(ref: Ligand, fit: Ligand, append_rsmd=True) -> Ligand:
    from asapdiscovery.data.backend.openeye import oechem

    fitmol = fit.to_oemol()
    refmol = ref.to_oemol()
    nConfs = fit.num_poses
    vecRmsd = oechem.OEDoubleArray(nConfs)
    success = oechem.OERMSD(refmol, fitmol, vecRmsd)
    if not success:
        print("RMSD calculation failed")

    if append_rsmd:
        fit.set_SD_data({"RMSD": list(vecRmsd)})
    return fit


def calculate_ligand_rmsd_oemol(ref: oechem.OEMol, fit: oechem.OEMol) -> float:
    return oechem.OERMSD(ref, fit)


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


def get_filtered_poses(results: list[POSITDockingResults], cutoff):
    """
    Filter out poses with RMSD above cutoff.
    Heavily based on code by Benjamin Kaminow.
    """

    # sort by pose id
    results.sort(key=lambda x: x.posed_ligand.conf_tags["Pose_ID"])
    all_oemols = [result.posed_ligand.to_oemol() for result in results]
    filtered_results_idx = []
    for i, oemol1 in enumerate(all_oemols):

        # Check if this oemol is similar to any already selected
        for idx in filtered_results_idx:
            oemol2 = all_oemols[idx]
            if calculate_ligand_rmsd_oemol(oemol1, oemol2) <= cutoff:
                # Similar to an already selected mol so don't need this one
                break
        else:
            # if not similar to any in filtered_results_idx, add index to list
            filtered_results_idx.append(i)

    # pull Ligand objects from indices
    filtered_results = [results[i] for i in filtered_results_idx]
    return filtered_results


def main():
    args = get_args()
    results_dir = args.results_dir

    args.output_file.mkdir(parents=True, exist_ok=True)

    mff = MolFileFactory(filename=args.ligands)
    ligs = mff.load()
    lig_dict = {lig.compound_name: lig for lig in ligs}

    # We don't want to filter across targets (at least at first)
    target_paths = list(results_dir.glob("docking_results/*"))
    filtered_results = []
    for target_path in target_paths:
        json_paths = list(target_path.glob("docking_result*.json"))
        results = [
            POSITDockingResults.from_json_file(json_file) for json_file in json_paths
        ]

        # First, filter based on cutoff
        filtered_results.extend(get_filtered_poses(results, args.cutoff))

    for result in tqdm(filtered_results):
        posed_lig = result.posed_ligand
        ref = lig_dict[posed_lig.compound_name]

        # no need to return anything because the posed_lig is modified directly
        calculate_ligand_rmsd(ref, posed_lig)

    df = make_df_from_docking_results(filtered_results)
    df.to_csv(args.output_file, index=False)


if __name__ == "__main__":
    main()
