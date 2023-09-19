import plotly.figure_factory as ff


def plot_kde(df, value_column, group_column, groups=None):
    """
    Plots a KDE plot of the values in `value_column` grouped by the values in `group_column`.
    :param df:
    :param value_column:
    :param group_column:
    :param groups:
    :return:
    """
    if not groups:
        groups = df[group_column].unique()
    arrays = [df[df[group_column] == group][value_column] for group in groups]
    fig = ff.create_distplot(arrays, group_labels=groups, bin_size=0.25, show_rug=False)
    fig.update_layout(width=600, height=400)
    fig.update_xaxes(title="RMSD (Å)", range=[0,8])
    fig.update_yaxes(title="Frequency", range=[0,1])
    return fig