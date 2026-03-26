"""
Visualization Script using Plotly Figure Factory with YAML configuration
This script generates a plotly figure from data,
using layout parameters specified in a YAML file.
"""

import click
import pandas as pd
import yaml
from plotly_utils import create_ecdf_figure
from pathlib import Path

PLOTLY_FUNCTION = {"chemical_similarity_ecdf": create_ecdf_figure}


@click.command()
@click.option("--input", "-i", required=True, help="Input CSV file with the data.")
@click.option(
    "--plot-type",
    required=True,
    help="Kind of plot to make, defined by the PLOTLY_FUNCTION",
)
@click.option(
    "--name",
    "-n",
    required=False,
    default=None,
    help="Name to use for the resulting figures, defaults to the name given in PLOTLY_FUNCTION",
)
@click.option(
    "--figure-dir",
    "-f",
    type=Path,
    required=False,
    default="figures",
    help="Directory to put the generated figures",
)
@click.option("--use-png", "-p", is_flag=True, help="Generate png file output")
@click.option("--use-html", "-h", is_flag=True, help="Generate html file output")
@click.option("--use-svg", "-s", is_flag=True, help="Generate svg file output")
@click.option("--config", "-c", help="YAML configuration file for plot layout.")
@click.option("--x-column", default="Tanimoto", help="Column name for x-axis values.")
@click.option(
    "--color-column",
    default="Similarity Metric",
    help="Column name for grouping/coloring.",
)
def create_plot(
    input,
    plot_type,
    name,
    figure_dir,
    use_png,
    use_html,
    use_svg,
    config,
    x_column,
    color_column,
):
    figure_factory = PLOTLY_FUNCTION.get(plot_type)
    if not figure_factory:
        raise NotImplementedError(
            f"{plot_type} not defined in PLOTLY_FUNCTION:\n{PLOTLY_FUNCTION}"
        )

    if not name:
        name = plot_type

    """Generate plot from a CSV file using Plotly with layout from YAML config."""
    try:
        with open(config, "r") as f:
            user_config = yaml.safe_load(f)
            if user_config:
                layout_config = user_config
        click.echo(f"Loaded configuration from {config}")
    except Exception as e:
        click.echo(f"Error loading config file: {e}", err=True)
        return

    # Read the data
    try:
        data = pd.read_csv(input)
        click.echo(f"Successfully loaded data from {input}")
    except Exception as e:
        click.echo(f"Error loading data: {e}", err=True)
        return

    # Validate columns exist
    if x_column not in data.columns:
        click.echo(f"Error: Column '{x_column}' not found in the data.", err=True)
        return
    if color_column not in data.columns:
        click.echo(f"Error: Column '{color_column}' not found in the data.", err=True)
        return

    # Create the figure
    fig = figure_factory(data, x_column, color_column, layout_config)

    # Save the figure
    try:
        if use_html:
            fig.write_html(figure_dir / f"{name}.html")
            # Also display the plot if run interactively
            click.echo(
                f"To view the plot in a browser, run: python -m webbrowser -t file://$(pwd)/{name}.html"
            )
        if use_png:
            fig.write_image(figure_dir / f"{name}.png")
        if use_svg:
            fig.write_image(figure_dir / f"{name}.svg")
        click.echo(f"Successfully saved plot")
    except Exception as e:
        click.echo(f"Error saving plot: {e}", err=True)
        return


if __name__ == "__main__":
    create_plot()
