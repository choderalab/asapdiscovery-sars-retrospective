"""
This script combines the results csvs and generates an input CSV that will be used to run the full cross docking evaluation.
"""

import pandas as pd
import argparse
from pathlib import Path
import numpy as np
from asapdiscovery.modeling.protein_prep import ProteinPrepper
import json


def get_args():
    parser = argparse.ArgumentParser(
        description="Combine results csvs and generate input csv for full cross docking evaluation"
    )
    parser.add_argument(
        "-r",
        "--results-dir",
        type=Path,
        required=True,
        help="Path to directory containing docking results",
    )
    parser.add_argument(
        "--protein-cache",
        type=Path,
        required=True,
        help="Path to directory containing prepped protein structures cache",
    )
    parser.add_argument(
        "--ligand-cache",
        type=Path,
        required=False,
        help="Path to directory containing prepped ligand cache. If false, protein cache will be used as ligand cache.",
    )
    parser.add_argument(
        "-d",
        "--data-path",
        type=Path,
        required=True,
        help="Path to directory containing additional data",
    )
    parser.add_argument(
        "--date-dict",
        type=Path,
        required=True,
        help="Path to date_dict.json file",
    )
    parser.add_argument(
        "--add-padding", action=argparse.BooleanOptionalAction, default=True
    )
    parser.add_argument(
        "-o", "--output-file", type=Path, required=True, help="Path to output file"
    )
    return parser.parse_args()


def main():
    args = get_args()

    # Load protein if protein cache is provided
    cache_source = args.protein_cache
    print(f"Loading prepped protein cache")
    complexes = ProteinPrepper.load_cache(cache_source)
    cmpd_to_frag_dict = {
        c.ligand.compound_name: c.target.target_name for c in complexes
    }

    if args.ligand_cache:
        print("Loading prepped ligand cache")
        ligand_cache = ProteinPrepper.load_cache(args.ligand_cache)
        cmpd_to_frag_dict.update(
            {c.ligand.compound_name: c.target.target_name for c in ligand_cache}
        )
    else:
        print(f"Using protein as both protein and ligand cache")

    with open("cmpd_to_frag_dict.json", "w") as f:
        json.dump(cmpd_to_frag_dict, f, indent=4)

    report_dict = {"err_msg": []}
    print("Loading csvs")
    dfs = [pd.read_csv(csv) for csv in args.results_dir.glob("*.csv")]
    df = pd.concat(dfs)
    query_lig_set = {lig for lig in df["Query_Ligand"]}
    ref_lig_set = {lig for lig in df["Reference_Ligand"]}
    report_dict["never_docked"] = list(ref_lig_set - query_lig_set)
    report_dict["never_used_as_ref"] = list(query_lig_set - ref_lig_set)

    if args.add_padding:
        print("Padding the data with the missing pairs")
        all_ligs = query_lig_set | ref_lig_set
        refs = df.Reference_Ligand
        queries = df.Query_Ligand
        pairs = {(ref, query) for ref, query in zip(refs, queries)}
        from itertools import permutations

        possible_pairs = set(list(permutations(all_ligs, 2)))

        missing_pairs = possible_pairs - pairs
        report_dict["missing_pairs"] = list(missing_pairs)
        null_df = pd.DataFrame(
            {
                "Reference_Ligand": [i for i, j in missing_pairs],
                "Query_Ligand": [j for i, j in missing_pairs],
                "RMSD": np.nan,
                "Pose_ID": 0,
                "POSIT_Method": "Failed",
            }
        )
        null_df["Reference_Structure"] = null_df.Reference_Ligand.apply(
            lambda x: cmpd_to_frag_dict[x]
        )

        padded = pd.concat([df, null_df])
        df = padded.copy()
        df = df.reindex()

        refs = df.Reference_Ligand
        queries = df.Query_Ligand
        pairs = {(ref, query) for ref, query in zip(refs, queries)}

        padding_success = len(pairs) == len(possible_pairs)
        report_dict["padding_success"] = padding_success
        if not padding_success:
            report_dict["err_msg"].append(
                f"Expected {len(possible_pairs)} pairs after padding, got {len(pairs)} pairs"
            )

    if not all(
        df["Reference_Structure"]
        == df.Reference_Ligand.apply(lambda x: cmpd_to_frag_dict[x])
    ):
        report_dict["err_msg"].append(
            "Reference_Structure column does not match cmpd_to_frag_dict"
        )

    df["Query_Structure"] = df.Query_Ligand.apply(lambda x: cmpd_to_frag_dict[x])

    # Add Date Information
    print("Adding date information")
    with open(args.date_dict, "r") as f:
        date_dict = json.load(f)
    missing = [
        ref_structure
        for ref_structure in df.Reference_Structure.unique()
        if ref_structure[:-3] not in date_dict.keys()
    ]
    if len(missing) > 0:
        report_dict["err_msg"].append(
            f"The following Reference_Structure were not in date_dict.json:"
        )
        report_dict["missing_reference_structures"] = missing

    df["Reference_Structure_Date"] = df.Reference_Structure.apply(
        lambda x: date_dict.get(x[:-3], None)
    )
    df["Query_Structure_Date"] = df.Query_Structure.apply(
        lambda x: date_dict.get(x[:-3], None)
    )

    # Add chemical similarity info
    print("Adding chemical similarity info")
    num_atoms_in_mcss = pd.read_csv(args.data_path / "20240503_mcss_num_atoms.csv")
    df = df.merge(
        num_atoms_in_mcss, on=["Query_Ligand", "Reference_Ligand"], how="left"
    )
    ecfp4_similarities = pd.read_csv(args.data_path / "20240503_all_tc_comparison.csv")
    df = df.merge(
        ecfp4_similarities, on=["Query_Ligand", "Reference_Ligand"], how="left"
    )

    # write output
    print("Write output")
    df.to_csv(args.output_file)

    with open(args.output_file.with_suffix(".json"), "w") as f:
        json.dump(report_dict, f, indent=4)


if __name__ == "__main__":
    main()
