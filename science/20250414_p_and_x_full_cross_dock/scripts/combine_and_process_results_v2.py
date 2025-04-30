"""
This script combines the results csvs and generates an input CSV that will be used to run the full cross docking evaluation.
"""

import pandas as pd
import argparse
from pathlib import Path
from asapdiscovery.data.schema.complex import PreppedComplex
from asapdiscovery.data.util.logging import FileLogger
import json
from pydantic import ValidationError
import yaml
from harbor.analysis.cross_docking import DockingDataModel


def get_args():
    parser = argparse.ArgumentParser(
        description="Combine results csvs and generate input csv for full cross docking evaluation"
    )
    parser.add_argument(
        "-i",
        "--input-csvs",
        required=True,
        nargs="+",
        help="One or more CSV files containing docking results",
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
        "--combined-chemical-similarity-csv",
        type=Path,
        required=True,
        help="Path to csv file containing combined chemical similarity data",
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
    parser.add_argument("--method-id", type=str, required=False)
    return parser.parse_args()


def load_cache(cache_source: Path) -> dict[str, str]:
    """Load protein/ligand cache and return compound to fragment mapping"""
    complexes = []
    for complex_path in cache_source.rglob("*.json"):
        try:
            complex_obj = PreppedComplex.from_json_file(complex_path)
            complexes.append(complex_obj)
        except ValidationError:
            continue

    return {c.ligand.compound_name: c.target.target_name for c in complexes}


def main():
    args = get_args()
    output_dir = args.output_dir
    output_dir.mkdir(exist_ok=True, parents=True)
    logger = FileLogger(
        logname="combine_and_process_results",
        path=output_dir / "combine_and_process_results.log",
    ).getLogger()

    # Load caches and create mapping
    logger.info("Loading prepped protein cache")
    cmpd_to_frag_dict = load_cache(args.protein_cache)

    if args.ligand_cache:
        logger.info("Loading prepped ligand cache")
        cmpd_to_frag_dict.update(load_cache(args.ligand_cache))
    else:
        logger.info("Using protein as both protein and ligand cache")

    with open(output_dir / "cmpd_to_frag_dict.json", "w") as f:
        json.dump(cmpd_to_frag_dict, f, indent=4)

    # Load and combine CSVs into DockingDataModel
    logger.info("Loading csvs")
    dfs = [pd.read_csv(csv) for csv in args.input_csvs]
    data = DockingDataModel(pd.concat(dfs))

    # Add structure information
    data.add_structure_mapping(cmpd_to_frag_dict)

    # Add padding if requested
    if args.add_padding:
        logger.info("Padding the data with missing pairs")
        data.add_missing_pairs()

    # Add dates
    logger.info("Adding date information")
    with open(args.date_dict, "r") as f:
        date_dict = json.load(f)
    data.add_dates(date_dict)

    # Add method ID if provided
    if args.method_id:
        logger.info("Adding method ID")
        data.add_method_id(args.method_id)

    # Save intermediate result
    logger.info("Writing intermediate output")
    data.to_csv(output_dir / f"{args.output_file_name}_no_chemical_similarity.csv")

    # Add chemical similarity information
    logger.info("Adding chemical similarity info")
    similarity_data = pd.read_csv(args.combined_chemical_similarity_csv)
    data.add_chemical_similarity(similarity_data)

    # Add scaffold information if provided
    if args.chemical_scaffold_data:
        logger.info("Adding chemical scaffold info")
        scaffold_data = pd.read_csv(args.chemical_scaffold_data)
        data.add_scaffold_information(scaffold_data)

    # Generate report
    report = data.generate_report()

    # Save final outputs
    logger.info("Writing output")
    data.to_csv(output_dir / f"{args.output_file_name}.csv")

    with open(output_dir / f"{args.output_file_name}_report.yaml", "w") as f:
        yaml.dump(report, f)


if __name__ == "__main__":
    main()