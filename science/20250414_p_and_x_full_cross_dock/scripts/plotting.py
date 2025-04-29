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
QUERY_SCAFFOLD_ID = "Query_Scaffold_ID_Subset_1"
REF_SCAFFOLD_ID = "Reference_Scaffold_ID_Subset_1"
COLOR_VAR = "Score"
STYLE_VAR = "Split"
CI_LOWER = "CI_Lower"
CI_UPPER = "CI_Upper"
LARGE_FIG_SIZE = (12, 8)
SMALL_FIG_SIZE = (8, 6)
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


# make some common click args
def fig_name_option():
    return click.option(
        "--fig-name",
        required=True,
        help="Output figure name",
    )


@cli.command("plot-filled-in-error-bars")
@click.argument("data-csv", type=click.Path(exists=True))
@click.option("--x-var", default=X_VAR, help="X variable")
@click.option("--y-var", default=Y_VAR, help="Y variable")
@click.option("--color-var", default=COLOR_VAR, help="Color variable")
@click.option("--style-var", default=STYLE_VAR, help="Style variable")
@click.option("--ci-lower", default=CI_LOWER, help="Lower confidence interval column")
@click.option("--ci-upper", default=CI_UPPER, help="Upper confidence interval column")
@fig_name_option()
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
    plt.figure(figsize=LARGE_FIG_SIZE)

    raw_df = pd.read_csv(data_csv)

    # need to sort for the values to make sense since we're plotting the lines manually
    raw_df = raw_df.sort_values(by=[x_var, color_var, style_var])

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
    plt.figure(figsize=LARGE_FIG_SIZE)

    # Create fill between for each group using matched colors
    for name, group in raw_df.groupby([color_var, style_var]):
        color_name = name[0]  # First element is Score
        plt.fill_between(
            group[x_var],
            group[ci_lower],
            group[ci_upper],
            color=color_map[color_name],
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
@click.argument("ligand-similarity-csv", type=click.Path(exists=True))
@click.option("--x-var", default="Tanimoto", help="X variable")
@fig_name_option()
def plot_similarity_ecdf(ligand_similarity_csv, x_var, fig_name):
    """Plot empirical cumulative distribution function for similarity data."""
    # Load data
    df = pd.read_csv(ligand_similarity_csv)

    # Filter based on most interesting
    df = df[df["bitsize"].isin([2048]) | df["bitsize"].isna()]
    df = df[df["radius"].isin([2, 5]) | df["radius"].isna()]

    color_var = "Similarity_Metric"

    # Create more readable labels
    label_map = {
        "ECFP_nan_2.0_2048.0": "ECFP4 Fingerprint",
        "ECFP_nan_5.0_2048.0": "ECFP10 Fingerprint",
        "MCS_nan_nan_nan": "N Atoms in MCS",
        "TanimotoCombo_False_nan_nan": "TanimotoCombo (Crystal Pose)",
        "TanimotoCombo_True_nan_nan": "TanimotoCombo (Maximum)",
    }

    # make a column that is the combination of the relevant variables
    # TODO: this is bad and hard-coded but to change it I'd have to go all the way back the chemical_similarity_schema
    df[color_var] = (
        df["Type"].astype(str)
        + "_"
        + df["Aligned"].astype(str)
        + "_"
        + df["radius"].astype(str)
        + "_"
        + df["bitsize"].astype(str)
    )
    df[color_var] = df[color_var].map(label_map)

    df = df.sort_values(by=[color_var, x_var], ascending=[False, True])

    # Create ECDF
    plt.figure(figsize=LARGE_FIG_SIZE)
    fig = sns.ecdfplot(df, x=x_var, hue=color_var, stat="proportion", linewidth=4)
    plt.xlabel("Tanimoto Similarity", fontsize=FONT_SIZES["xlabel"], fontweight="bold")
    plt.ylabel(
        "Fraction of Pairwise\n Ligand Similarities",
        fontsize=FONT_SIZES["ylabel"],
        fontweight="bold",
    )

    # tick text
    plt.xticks(fontsize=FONT_SIZES["ticks"])
    plt.yticks(fontsize=FONT_SIZES["ticks"])

    # for legend text
    plt.setp(fig.get_legend().get_texts(), fontsize=FONT_SIZES["legend_text"])
    plt.setp(fig.get_legend().get_title(), fontsize=FONT_SIZES["legend_title"])

    plt.tight_layout()

    plt.savefig(fig_name + ".svg", format="svg", bbox_inches="tight")
    plt.savefig(fig_name + ".png", format="png", bbox_inches="tight")


@cli.command("plot-scaffold-heatmap")
@click.argument("scaffold-similarity-csv", type=click.Path(exists=True))
@click.option("--ref", default=QUERY_SCAFFOLD_ID)
@click.option("--query", default=REF_SCAFFOLD_ID)
@click.option("--groupby", default=["Score", "Split"], multiple=True)
@fig_name_option()
def plot_scaffold_heatmap(scaffold_similarity_csv, ref, query, groupby, fig_name):
    raw_df = pd.read_csv(scaffold_similarity_csv)

    # replace brackets in the query and ref columns
    raw_df[query] = (
        raw_df[query]
        .astype(str)
        .apply(lambda x: x.replace("[", "").replace("]", "") if "[" in x else x)
    )
    raw_df["qint"] = raw_df[query].astype(float)
    raw_df[ref] = (
        raw_df[ref]
        .astype(str)
        .apply(lambda x: x.replace("[", "").replace("]", "") if "[" in x else x)
    )
    raw_df["rint"] = raw_df[ref].astype(float)

    heatmap_dfs = {
        "_".join(name): group for name, group in raw_df.groupby(list(groupby))
    }

    for name, heatmap_df in heatmap_dfs.items():
        pivot_fraction = heatmap_df.pivot(
            index="qint", columns="rint", values="Fraction"
        )
        ref_counts = (
            heatmap_df.sort_values("rint")
            .groupby(ref)
            .head(1)[[ref, "Total"]]
            .to_dict(orient="records")
        )
        count_dict = {data[ref]: data["Total"] for data in ref_counts}
        ytick_labels = [
            f"$\\bf{cluster_id}$ ({total})" for cluster_id, total in count_dict.items()
        ]
        xtick_labels = [
            f"$\\bf{cluster_id}$\n({total})" for cluster_id, total in count_dict.items()
        ]
        plt.figure(figsize=LARGE_FIG_SIZE)
        heatmap = sns.heatmap(
            data=pivot_fraction,
            xticklabels=xtick_labels,
            yticklabels=ytick_labels,
            annot=True,
            cmap="coolwarm_r",
        )
        # Add colorbar label
        heatmap.collections[0].colorbar.set_label("Fraction")

        # Rotate axis labels for better readability
        plt.xticks(rotation=0)
        plt.yticks(rotation=0)

        # Invert y-axis to put 0 at bottom
        plt.gca().invert_yaxis()

        # Set axis labels
        plt.xlabel(
            f"Reference Scaffold Cluster ID",
            fontsize=FONT_SIZES["xlabel"],
            fontweight="bold",
        )
        plt.ylabel(
            f"Query Scaffold Cluster ID",
            fontsize=FONT_SIZES["ylabel"],
            fontweight="bold",
        )
        plt.title(
            f"{name}",
            fontsize=FONT_SIZES["xlabel"],
            fontweight="bold",
        )

        plt.savefig(fig_name + name + ".svg", format="svg", bbox_inches="tight")
        plt.savefig(fig_name + name + ".png", format="png", bbox_inches="tight")


if __name__ == "__main__":
    cli()
