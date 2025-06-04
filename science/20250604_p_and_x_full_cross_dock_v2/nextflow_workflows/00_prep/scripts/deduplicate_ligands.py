#!/usr/bin/env python
import click

"""
Example usage:
python deduplicate_ligands.py \
    --fragalysis-dir /data1/choderaj/paynea/asap-datasets/full_cross_dock_v2/mpro_fragalysis-04-01-24_curated \
    --prepped-path /data1/choderaj/paynea/asap-datasets/full_cross_dock_v2/mpro_fragalysis-04-01-24_curated_cache \
    --output-dir /data1/choderaj/paynea/asap-datasets/full_cross_dock_v2/mpro_fragalysis-04-01-24_curated_cache_fixed
"""
from pathlib import Path
import pandas as pd
from datetime import datetime
import shutil
from asapdiscovery.modeling.protein_prep import PreppedComplex


def date_processor(date_string):
    if isinstance(date_string, str) and date_string != "None":
        try:
            return datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return datetime.strptime(date_string, "%d/%m/%Y %H:%M")
    return None


def process_crystal_data(soaks):
    ddf = soaks.loc[:, ["Sample Name", "Data Collection Date"]]
    ddf["Sanitized_Date"] = ddf["Data Collection Date"].apply(date_processor)
    ddf.columns = ["Structure_Name", "Data_Collection_Date", "Structure_Date"]
    date_dict = ddf.set_index("Structure_Name").to_dict()["Structure_Date"]
    date_dict = {k: str(v) for k, v in date_dict.items() if str(v) != "NaT"}
    return date_dict


def get_records_from_complexes(complexes):
    records = []
    for c in complexes:
        records.append(
            {
                "SMILES": c.ligand.smiles,
                "Compound_Name": c.ligand.compound_name,
                "Target_Name": c.target.target_name,
            }
        )
    return records


@click.command()
@click.option(
    "--fragalysis-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    required=True,
    help="Directory containing Fragalysis data",
)
@click.option(
    "--prepped-path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    required=True,
    help="Directory containing prepped complexes",
)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, dir_okay=True),
    required=True,
    help="Output directory for filtered structures",
)
def main(fragalysis_dir, prepped_path, output_dir):
    """Filter and copy protein structures based on deduplication criteria."""
    pcs_to_load = list(prepped_path.glob("./*/*.json"))
    if not pcs_to_load:
        click.echo("No prepped complexes found to load.")
        return

    click.echo(f"Found {len(pcs_to_load)} prepped complexes to load.")

    # Load Fragalysis data
    pcs = [PreppedComplex.from_json_file(f) for f in pcs_to_load]

    # Create initial dataframe
    df = pd.DataFrame.from_records(get_records_from_complexes(pcs))

    # Get duplicated SMILES
    smiles_counts = df.groupby("SMILES").nunique()
    dup_smiles = smiles_counts[
        (smiles_counts["Compound_Name"] > 1) | (smiles_counts["Target_Name"] > 1)
    ].index

    # Process duplicates
    ordered_df = df[df.SMILES.isin(dup_smiles)].sort_values(["SMILES", "Target_Name"])

    # Load and process dates
    soaks_path = Path(fragalysis_dir) / "extra_files" / "Mpro_soaks.csv"
    soaks = pd.read_csv(soaks_path)
    date_dict = process_crystal_data(soaks)

    # Add dates and find structures to keep
    ordered_df["Date"] = ordered_df.Target_Name.apply(lambda x: date_dict[x[:-3]])
    to_keep = ordered_df.sort_values("Date").groupby(["SMILES"]).head(1)
    targets_to_keep = set(to_keep.Target_Name.unique())
    all_duped_targets = set(ordered_df.Target_Name.unique())
    targets_to_remove = all_duped_targets - targets_to_keep

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Copy files, skipping removed targets
    prepped_path = Path(prepped_path)
    copied = 0
    skipped = 0

    for src_path in prepped_path.glob("*/*.json"):
        target_name = src_path.parent.name
        # Check if the target should be removed (starts with any name in targets_to_remove)
        if not any(target_name.startswith(x[:-3]) for x in targets_to_remove):
            dest_dir = output_path / src_path.parent.name
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dest_dir / src_path.name)
            copied += 1
        else:
            skipped += 1

    click.echo(f"Copied {copied} files")
    click.echo(f"Skipped {skipped} files")
    click.echo(f"Total files processed: {copied + skipped}")


if __name__ == "__main__":
    main()
