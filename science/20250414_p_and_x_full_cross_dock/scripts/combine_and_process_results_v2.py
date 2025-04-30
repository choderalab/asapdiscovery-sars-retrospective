"""
This script combines the results csvs and generates an input CSV that will be used to run the full cross docking evaluation.
"""

import click
import pandas as pd
from pathlib import Path
from asapdiscovery.data.schema.complex import PreppedComplex
from asapdiscovery.data.util.logging import FileLogger
import json
from pydantic import ValidationError
import yaml
from cross_docking.models import DockingDataModel


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


@click.command()
@click.option(
    "-i",
    "--input-csvs",
    required=True,
    multiple=True,
    help="One or more CSV files containing docking results",
    type=click.Path(exists=True, path_type=Path)
)
@click.option(
    "--protein-cache",
    required=True,
    help="Path to directory containing prepped protein structures cache",
    type=click.Path(exists=True, path_type=Path)
)
@click.option(
    "--ligand-cache",
    required=False,
    help="Path to directory containing prepped ligand cache. If false, protein cache will be used as ligand cache.",
    type=click.Path(exists=True, path_type=Path)
)
@click.option(
    "-d",
    "--combined-chemical-similarity-csv",
    required=True,
    help="Path to csv file containing combined chemical similarity data",
    type=click.Path(exists=True, path_type=Path)
)
@click.option(
    "--date-dict",
    required=True,
    help="Path to date_dict.json file",
    type=click.Path(exists=True, path_type=Path)
)
@click.option(
    "--chemical-scaffold-data",
    required=False,
    help="Path to chemical scaffold data",
    type=click.Path(exists=True, path_type=Path)
)
@click.option(
    "--add-padding/--no-add-padding",
    default=True,
    help="Whether to add padding for missing pairs"
)
@click.option(
    "--output-dir",
    required=True,
    help="Path to output directory",
    type=click.Path(path_type=Path)
)
@click.option(
    "--output-file-name",
    required=True,
    help="Name of the output file",
    type=str
)
@click.option(
    "--method-id",
    required=False,
    help="Method ID to add to the output",
    type=str
)
def main(
    input_csvs: tuple[Path],
    protein_cache: Path,
    ligand_cache: Path | None,
    combined_chemical_similarity_csv: Path,
    date_dict: Path,
    chemical_scaffold_data: Path | None,
    add_padding: bool,
    output_dir: Path,
    output_file_name: str,
    method_id: str | None
):
    """Combine results csvs and generate input csv for full cross docking evaluation"""
    output_dir.mkdir(exist_ok=True, parents=True)
    logger = FileLogger(
        logname="combine_and_process_results",
        path=output_dir / "combine_and_process_results.log",
    ).getLogger()

    # Load caches and create mapping
    logger.info("Loading prepped protein cache")
    cmpd_to_frag_dict = load_cache(protein_cache)

    if ligand_cache:
        logger.info("Loading prepped ligand cache")
        cmpd_to_frag_dict.update(load_cache(ligand_cache))
    else:
        logger.info("Using protein as both protein and ligand cache")

    with open(output_dir / "cmpd_to_frag_dict.json", "w") as f:
        json.dump(cmpd_to_frag_dict, f, indent=4)

    # Load and combine CSVs into DockingDataModel
    logger.info("Loading csvs")
    dfs = [pd.read_csv(csv) for csv in input_csvs]
    data = DockingDataModel(pd.concat(dfs))

    # Add structure information
    data.add_structure_mapping(cmpd_to_frag_dict)

    # Add padding if requested
    if add_padding:
        logger.info("Padding the data with missing pairs")
        data.add_missing_pairs()

    # Add dates
    logger.info("Adding date information")
    with open(date_dict, "r") as f:
        date_dict_data = json.load(f)
    data.add_dates(date_dict_data)

    # Add method ID if provided
    if method_id:
        logger.info("Adding method ID")
        data.add_method_id(method_id)

    # Save intermediate result
    logger.info("Writing intermediate output")
    data.to_csv(output_dir / f"{output_file_name}_no_chemical_similarity.csv")

    # Add chemical similarity information
    logger.info("Adding chemical similarity info")
    similarity_data = pd.read_csv(combined_chemical_similarity_csv)
    data.add_chemical_similarity(similarity_data)

    # Add scaffold information if provided
    if chemical_scaffold_data:
        logger.info("Adding chemical scaffold info")
        scaffold_data = pd.read_csv(chemical_scaffold_data)
        data.add_scaffold_information(scaffold_data)

    # Generate report
    report = data.generate_report()

    # Save final outputs
    logger.info("Writing output")
    data.to_csv(output_dir / f"{output_file_name}.csv")

    with open(output_dir / f"{output_file_name}_report.yaml", "w") as f:
        yaml.dump(report, f)


if __name__ == "__main__":
    main()