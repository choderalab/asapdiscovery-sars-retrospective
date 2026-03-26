import pandas as pd
import glob
import os
import click


@click.command()
@click.option(
    "--input-path",
    "-i",
    required=True,
    type=click.Path(exists=True),
    help="Directory containing CSV files",
)
@click.option(
    "--output-file", "-o", required=True, type=click.Path(), help="Output CSV file path"
)
@click.option(
    "--pattern",
    "-p",
    default="*.csv",
    help="Glob pattern for CSV files (default: *.csv)",
)
def combine_csv_files(input_path, output_file, pattern):
    """Combine multiple CSV files into a single CSV file."""
    # Get all CSV files in the directory
    csv_files = glob.glob(os.path.join(input_path, pattern))

    if not csv_files:
        click.echo(f"No CSV files found in {input_path} matching pattern {pattern}")
        return

    # Create empty list to store dataframes
    dfs = []

    # Read each CSV file and append to list
    for file in csv_files:
        df = pd.read_csv(file)
        df["source_file"] = os.path.basename(file)
        dfs.append(df)

    # Combine all dataframes
    combined_df = pd.concat(dfs, ignore_index=True)

    # Save combined dataframe
    combined_df.to_csv(output_file, index=False)
    click.echo(f"Combined {len(csv_files)} files into {output_file}")


if __name__ == "__main__":
    combine_csv_files()
