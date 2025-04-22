import pandas as pd
import glob
import os
import click


@click.command()
@click.option(
    "--input-path",
    "-i",
    required=False,
    default=None,
    type=click.Path(exists=True),
    help="Directory containing CSV files",
)
@click.option(
    "--input-csvs",
    "-c",
    required=False,
    multiple=True,
    default=None,
    type=click.Path(exists=True),
    help="One or more CSV files containing docking results",
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
def combine_csv_files(input_path, input_csvs, output_file, pattern):
    """Combine multiple CSV files into a single CSV file."""

    if not input_path and not input_csvs:
        raise click.BadParameter(
            "Either --input-path or --input-csvs must be provided."
        )
    if input_path and input_csvs:
        raise click.BadParameter(
            "Only one of --input-path or --input-csvs can be provided."
        )

    if input_csvs:
        # If input_csvs is provided, use it directly
        csv_files = list(input_csvs)

    else:
        # Get all CSV files in the directory
        csv_files = glob.glob(os.path.join(input_path, pattern))

        if not csv_files:
            raise FileNotFoundError(
                f"No CSV files found in {input_path} matching pattern {pattern}"
            )

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
