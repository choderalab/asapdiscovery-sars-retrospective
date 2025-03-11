"""
This script combines the results csvs and generates an input CSV that will be used to run the full cross docking evaluation.
"""

import pandas as pd
import argparse
from pathlib import Path
import numpy as np
from asapdiscovery.data.schema.complex import PreppedComplex
from asapdiscovery.data.util.logging import FileLogger
import json
from pydantic import ValidationError


def get_args():
    parser = argparse.ArgumentParser(
        description="Combine results csvs and generate input csv for full cross docking evaluation"
    )
    parser.add_argument(
        "-r",
        "--results-dir",
        type=Path,
        required=True,
        help="Path to directory containing docking results, each file should be a csv and there shouldn't be any csv files you don't want included.",
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
    parser.add_argument("--chemical-scaffold-data", type=Path, required=False)
    parser.add_argument(
        "--add-padding", action=argparse.BooleanOptionalAction, default=True
    )
    parser.add_argument(
        "--output-dir", type=Path, required=True, help="Path to output directory"
    )
    parser.add_argument("--output-file-name", type=str, required=True)
    return parser.parse_args()


def load_cache(cache_source):
    complexes = []
    for complex_path in cache_source.rglob("*.json"):
        try:
            complex_obj = PreppedComplex.from_json_file(complex_path)
            complexes.append(complex_obj)
        except ValidationError as e:
            print(f"Failed to load {complex_path}")

    return complexes


def main():
    args = get_args()
    output_dir = args.output_dir
    output_dir.mkdir(exist_ok=True, parents=True)
    logger = FileLogger(
        logname="combine_and_process_results",
        path=output_dir / "combine_and_process_results.log",
    ).getLogger()

    # Load protein cache
    logger.info("Loading prepped protein cache")

    complexes = load_cache(args.protein_cache)
    cmpd_to_frag_dict = {
        c.ligand.compound_name: c.target.target_name for c in complexes
    }

    if args.ligand_cache:
        logger.info("Loading prepped ligand cache")
        ligand_cache = load_cache(args.ligand_cache)
        cmpd_to_frag_dict.update(
            {c.ligand.compound_name: c.target.target_name for c in ligand_cache}
        )
    else:
        logger.info(f"Using protein as both protein and ligand cache")

    with open(output_dir / "cmpd_to_frag_dict.json", "w") as f:
        json.dump(cmpd_to_frag_dict, f, indent=4)

    report_dict = {"err_msg": []}
    logger.info("Loading csvs")
    dfs = [pd.read_csv(csv) for csv in args.results_dir.glob("*.csv")]
    df = pd.concat(dfs)
    query_lig_set = {lig for lig in df["Query_Ligand"]}
    ref_lig_set = {lig for lig in df["Reference_Ligand"]}
    report_dict["never_docked"] = list(ref_lig_set - query_lig_set)
    report_dict["never_used_as_ref"] = list(query_lig_set - ref_lig_set)

    if args.add_padding:
        logger.info("Padding the data with the missing pairs")
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
    logger.info("Adding date information")
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

    logger.info("Writing intermediate_output")
    df.to_csv(output_dir / f"{args.output_file_name}_no_chemical_similarity.csv")

    # Add chemical similarity info
    logger.info("Adding chemical similarity info")
    combined_chemical_similarity_info = pd.read_csv(
        args.data_path / "combined_data.csv"
    )
    df = df.merge(
        combined_chemical_similarity_info,
        on=["Query_Ligand", "Reference_Ligand"],
        how="left",
    )

    if args.chemical_scaffold_data:
        logger.info("Adding chemical scaffold info")
        scaffold_info = pd.read_csv(args.chemical_scaffold_data)
        df = df.merge(
            scaffold_info,
            left_on="Query_Ligand",
            right_on="compound_name",
            how="left",
            suffixes=(None, "_Query"),
        )
        df = df.merge(
            scaffold_info,
            left_on="Reference_Ligand",
            right_on="compound_name",
            how="left",
            suffixes=(None, "_Reference"),
        )

    # write output
    logger.info("Writing output")
    final_output_file = output_dir / args.output_file_name
    df.to_csv(final_output_file)

    with open(final_output_file.with_suffix("_report.json"), "w") as f:
        json.dump(report_dict, f, indent=4)


if __name__ == "__main__":
    main()
