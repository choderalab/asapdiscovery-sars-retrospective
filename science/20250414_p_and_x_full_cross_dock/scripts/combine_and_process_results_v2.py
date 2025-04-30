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
from harbor.analysis.cross_docking import DataFrameModel, DataFrameType, DockingDataModel
import numpy as np

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
    report_dict = {"err_msg": []}
    logger.info("Loading csvs")
    dfs = [pd.read_csv(csv) for csv in input_csvs]
    df = pd.concat(dfs)

    query_lig_set = {lig for lig in df["Query_Ligand"]}
    ref_lig_set = {lig for lig in df["Reference_Ligand"]}
    report_dict["never_docked"] = list(ref_lig_set - query_lig_set)
    report_dict["never_used_as_ref"] = list(query_lig_set - ref_lig_set)

    # Add padding if requested
    if add_padding:
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
    if not all(df["Reference_Structure"]== df.Reference_Ligand.apply(lambda x: cmpd_to_frag_dict[x])):
        report_dict["err_msg"].append(
            "Reference_Structure column does not match cmpd_to_frag_dict"
        )

    df["Query_Structure"] = df.Query_Ligand.apply(lambda x: cmpd_to_frag_dict[x])

    # Add Date Information
    logger.info("Adding date information")
    with open(date_dict, "r") as f:
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

    # Add Method ID
    if method_id:
        logger.info("Adding method ID")
        df["Method_ID"] = method_id

    logger.info("Writing intermediate_output")
    df.to_csv(output_dir / f"{output_file_name}_no_chemical_similarity.csv")

    # Add chemical similarity info
    logger.info("Adding chemical similarity info")
    combined_chemical_similarity_info = pd.read_csv(
        combined_chemical_similarity_csv
    )
    df = df.merge(
        combined_chemical_similarity_info,
        on=["Query_Ligand", "Reference_Ligand"],
        how="left",
    )

    if chemical_scaffold_data:
        logger.info("Adding chemical scaffold info")
        scaffold_info = pd.read_csv(chemical_scaffold_data)
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
    # construct Data
    pose_data = DataFrameModel(dataframe=df, type=DataFrameType.POSE, key_columns=["Query_Ligand", "Reference_Structure", "Pose_ID"])
    ref_data = DataFrameModel(dataframe=df, type=DataFrameType.REFERENCE, key_columns=["Reference_Structure"])
    lig_data = DataFrameModel(dataframe=df, type=DataFrameType.QUERY, key_columns=["Query_Structure"])
    similarity_data = DataFrameModel(dataframe=df, type=DataFrameType.CHEMICAL_SIMILARITY, key_columns=["Query_Structure", "Reference_Structure", "Aligned", "radius", "bitsize", "fingerprint"])
    scaffold_data = DataFrameModel(dataframe=df, type=DataFrameType.CHEMICAL_SIMILARITY, key_columns=["Query_Ligand", "Reference_Ligand"])
    data = DockingDataModel.from_models([pose_data, ref_data, lig_data, similarity_data, scaffold_data])

    # write output
    logger.info("Writing output")
    data.serialize(output_dir / output_file_name)

    output_report = output_dir / f"{output_file_name}_report.yaml"
    with open(output_report, "w") as f:
        yaml.dump(report_dict, f)


if __name__ == "__main__":
    main()