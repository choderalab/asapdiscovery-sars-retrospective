import pandas as pd
import glob
import os
import click


@click.command()
@click.argument(
    "--input-csvs",
    "-c",
    nargs=-1,
    type=click.Path(exists=True),
    help="One or more CSV files containing docking results",
)
@click.argument("--output-file", "-o", type=click.Path(), help="Output CSV file path")
def combine_csv_files(input_path, input_csvs, output_file, pattern):
    """Combine multiple CSV files into a single CSV file."""
    csv_files = list(input_csvs)

    # Create empty list to store dataframes
    dfs = []

    # Read each CSV file and append to list
    for file in csv_files:
        df = pd.read_csv(file)
        dfs.append(df)

    # Combine all dataframes
    combined_df = pd.concat(dfs, ignore_index=True)

    # Save combined dataframe
    combined_df.to_csv(output_file, index=False)
    click.echo(f"Combined {len(csv_files)} files into {output_file}")


if __name__ == "__main__":
    combine_csv_files()
