from matplotlib.ticker import ScalarFormatter
import matplotlib.pyplot as plt
import seaborn as sns
import click
import pandas as pd

# Global configuration
X_VAR = "N_Per_Split"
Y_VAR = "Fraction"
X_LABEL = "Number of Reference Structures Available to Use"
Y_LABEL = "Fraction of Ligands Posed \n<2Å from Reference"
COLOR_VAR = "Score"
STYLE_VAR = "Split"
CI_LOWER = "CI_Lower"
CI_UPPER = "CI_Upper"
FIG_SIZE = (12, 8)
FONT_SIZES = {
    "xlabel": 24,
    "ylabel": 24,
    "ticks": 18,
    "legend_title": 24,
    "legend_text": 18,
}
ALPHA = 0.2


@click.group()
def cli():
    """Collection of plotting commands."""
    pass


@cli.command("plot-filled-in-error-bars")
@click.argument("data-csv")
@click.option("--x-var", default=X_VAR, help="X variable")
@click.option("--y-var", default=Y_VAR, help="Y variable")
@click.option("--color-var", default=COLOR_VAR, help="Color variable")
@click.option("--style-var", default=STYLE_VAR, help="Style variable")
@click.option("--ci-lower", default=CI_LOWER, help="Lower confidence interval column")
@click.option("--ci-upper", default=CI_UPPER, help="Upper confidence interval column")
@click.option("--fig-name", required=True, help="Output figure name")
def plot_filled_in_error_bars(
    data_csv,
    x_var,
    y_var,
    color_var,
    style_var,
    ci_lower,
    ci_upper,
    fig_name,
):
    """Plot filled-in error bars with seaborn for the given DATA_CSV"""
    plt.figure(figsize=FIG_SIZE)

    raw_df = pd.read_csv(data_csv)

    # First create the main plot to get the color mapping
    fig = sns.lineplot(
        data=raw_df,
        x=x_var,
        y=y_var,
        hue=color_var,
        style=style_var,
    )

    # Get the color mapping
    legend = plt.gca().get_legend()
    color_map = {
        text._text: line.get_color()
        for line, text in zip(legend.get_lines(), legend.get_texts())
    }

    # Clear the plot to start fresh
    plt.clf()
    plt.figure(figsize=FIG_SIZE)

    # Create fill between for each group using matched colors
    for name, group in raw_df.groupby([color_var, style_var]):
        score = name[0]  # First element is Score
        plt.fill_between(
            group[x_var],
            group[ci_lower],
            group[ci_upper],
            color=color_map[score],
            alpha=ALPHA,
        )

    # Recreate the main plot
    fig = sns.lineplot(
        data=raw_df,
        x=x_var,
        y=y_var,
        hue=color_var,
        style=style_var,
    )

    plt.xlabel(X_LABEL, fontsize=FONT_SIZES["xlabel"], fontweight="bold")
    plt.ylabel(Y_LABEL, fontsize=FONT_SIZES["ylabel"], fontweight="bold")

    plt.xscale("log")
    plt.gca().xaxis.set_major_formatter(ScalarFormatter())

    custom_ticks = [1, 5, 10, 20, 50, 100, 200, raw_df[x_var].max()]
    plt.xticks(custom_ticks, custom_ticks, fontsize=FONT_SIZES["ticks"])
    plt.yticks(fontsize=FONT_SIZES["ticks"])

    legend = plt.legend()
    plt.setp(legend.get_title(), fontsize=FONT_SIZES["legend_title"], fontweight="bold")
    plt.setp(legend.get_texts(), fontsize=FONT_SIZES["legend_text"])

    plt.tight_layout()

    plt.savefig(fig_name + ".svg", format="svg", bbox_inches="tight")
    plt.savefig(fig_name + ".png", format="png", bbox_inches="tight")


@cli.command("plot-similarity-ecdf")
@click.option("--input-file", required=True, help="Input data file")
@click.option("--fig-name", required=True, help="Output figure name")
def plot_similarity_ecdf(input_file, fig_name):
    """Plot empirical cumulative distribution function for similarity data."""
    # Implement ECDF plotting logic here
    pass


if __name__ == "__main__":
    cli()
