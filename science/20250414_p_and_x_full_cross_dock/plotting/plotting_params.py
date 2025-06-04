import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import seaborn as sns
from pathlib import Path

# Global configuration
sns.set_style("white")

X_VAR = "N_Reference_Structures"
Y_VAR = "Fraction"
X_LABEL = "Number of Reference Structures Available to Use \n(Log Scale)"
Y_LABEL = "Fraction of Ligands Posed \n<2Å from Reference"
QUERY_SCAFFOLD_ID = "Query_Scaffold_ID_Subset_1"
REF_SCAFFOLD_ID = "Reference_Scaffold_ID_Subset_1"
COLOR_VAR = "Reference_Split"
STYLE_VAR = "Score"
CI_LOWER = "CI_Lower"
CI_UPPER = "CI_Upper"
label_map = {
    "Reference_Split": "Dataset Split Type",
    "Score": "Scoring Method",
    "RandomSplit": "Randomly Ordered",
    "DateSplit": "Ordered by Date",
    "RMSD": "RMSD (Positive Control)",
    "POSIT_Probability": "POSIT Probability",
    "N_Reference_Structures": "Number of Randomly Chosen Reference Structures"
}
LARGE_FIG_SIZE = (12, 8)
SMALL_FIG_SIZE = (8, 6)
FONT_SIZES = {
    "xlabel": 24,
    "ylabel": 24,
    "ticks": 18,
    "legend_title": 24,
    "legend_text": 18,
}
ALPHA = 0.1


# plotting functions


def update_figure(
    plt,
    raw_df,
    label_map={},
    x_var=X_VAR,
    legend_title="",
    color_var=COLOR_VAR,
    style_var=STYLE_VAR,
    legend_subtitles=[],
):
    # Create a function to map labels
    def get_label(var):
        return label_map.get(var, var)

    # After creating the plot
    handles, labels = plt.gca().get_legend_handles_labels()
    plt.legend(handles[::-1], labels[::-1])

    plt.xlabel(get_label(X_LABEL), fontsize=FONT_SIZES["xlabel"], fontweight="bold")
    plt.ylabel(get_label(Y_LABEL), fontsize=FONT_SIZES["ylabel"], fontweight="bold")

    plt.xscale("log")
    plt.gca().xaxis.set_major_formatter(ScalarFormatter())

    custom_ticks = [1, 5, 10, 20, 50, 100, 200, raw_df[x_var].max()]
    plt.xticks(custom_ticks, custom_ticks, fontsize=FONT_SIZES["ticks"])
    plt.yticks(fontsize=FONT_SIZES["ticks"])

    # Update legend labels
    legend = plt.legend(title=legend_title)  # Map legend title
    texts = legend.get_texts()

    # Update legend text with mapped values
    for text in texts:
        if text._text in [color_var, style_var]:
            plt.setp(text, fontsize=FONT_SIZES["legend_title"], fontweight="bold")
        text.set_text(get_label(text._text))

    plt.setp(legend.get_title(), fontsize=FONT_SIZES["legend_title"], fontweight="bold")
    plt.setp(legend.get_texts(), fontsize=FONT_SIZES["legend_text"])

    plt.tight_layout()
    return plt


# %%
def update_labels(
    fig,
    label_map,
    x_label=X_LABEL,
    y_label=Y_LABEL,
    legend_title=None,
    legend_subtitles=[],
    ignore_legend = False,
):
    def get_label(var):
        return label_map.get(var, var)

    # Get the current axes from the figure
    ax = fig.gca()

    # After creating the plot
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1])

    ax.set_xlabel(get_label(x_label), fontsize=FONT_SIZES["xlabel"], fontweight="bold")
    ax.set_ylabel(get_label(y_label), fontsize=FONT_SIZES["ylabel"], fontweight="bold")

    plt.yticks(fontsize=FONT_SIZES["ticks"])
    plt.xticks(fontsize=FONT_SIZES["ticks"])
    
    # Update legend labels
    legend = ax.legend(title=legend_title)  # Map legend title
    texts = legend.get_texts()

    # Update legend text with mapped values
    for text in texts:
        if text._text in legend_subtitles:
            plt.setp(text, fontsize=FONT_SIZES["legend_title"], fontweight="bold")
        text.set_text(get_label(text._text))

    plt.setp(legend.get_title(), fontsize=FONT_SIZES["legend_title"], fontweight="bold")
    plt.setp(legend.get_texts(), fontsize=FONT_SIZES["legend_text"])

    plt.tight_layout()
    return fig


# %%
def save_figure(plt, fig_path: Path):
    plt.savefig(
        fig_path.with_suffix(".svg"), format="svg", bbox_inches="tight", dpi=200
    )
    plt.savefig(fig_path.with_suffix(".png"), bbox_inches="tight", dpi=200)


# %%
def figure_decorator(
    func, raw_df, fig_path: Path, label_map={}, x_var=X_VAR, legend_title="", **kwargs
):
    fig = func(raw_df=raw_df, x_var=x_var, **kwargs)
    update_figure(fig, raw_df, label_map, x_var, legend_title)
    save_figure(fig, fig_path)


# %%
def plot_filled_in_error_bars(
    raw_df,
    x_var=X_VAR,
    y_var=Y_VAR,
    color_var=COLOR_VAR,
    style_var=STYLE_VAR,
    ci_lower=CI_LOWER,
    ci_upper=CI_UPPER,
):
    """Plot filled-in error bars with seaborn for the given DATA_CSV"""

    # Sort the dataframe
    raw_df = raw_df.sort_values(by=[x_var, style_var, color_var])

    # First create the main plot to get the color and style mapping
    sns.lineplot(
        data=raw_df,
        x=x_var,
        y=y_var,
        hue=color_var,
        style=style_var,
        hue_order=list(reversed(sorted(raw_df[color_var].unique()))),
        style_order=list(reversed(sorted(raw_df[style_var].unique()))),
    )

    # Get the mappings
    legend = plt.gca().get_legend()
    color_map = {}
    style_map = {}
    for line, text in zip(legend.get_lines(), legend.get_texts()):
        color_map[text._text] = line.get_color()
        style_map[text._text] = (line.get_linestyle(), line.get_marker())

    # Clear the plot to start fresh
    plt.clf()
    plt.figure(figsize=LARGE_FIG_SIZE)

    # Create fill between and styled boundary lines for each group
    for name, group in raw_df.groupby([color_var, style_var]):
        color_name, style_name = name
        color = color_map[color_name]
        linestyle, marker = style_map[style_name]

        plt.fill_between(
            group[x_var],
            group[ci_lower],
            group[ci_upper],
            color=color,
            alpha=ALPHA,
        )

        plt.plot(
            group[x_var],
            group[ci_lower],
            color=color,
            linestyle=linestyle,
            marker=marker,
            alpha=ALPHA * 2,
        )
        plt.plot(
            group[x_var],
            group[ci_upper],
            color=color,
            linestyle=linestyle,
            marker=marker,
            alpha=ALPHA * 2,
        )

    # Recreate the main plot with mapped labels
    sns.lineplot(
        data=raw_df,
        x=x_var,
        y=y_var,
        hue=color_var,
        style=style_var,
        hue_order=list(reversed(sorted(raw_df[color_var].unique()))),
        style_order=list(reversed(sorted(raw_df[style_var].unique()))),
    )
    return plt
