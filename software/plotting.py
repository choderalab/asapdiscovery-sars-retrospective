import plotly.figure_factory as ff
from plotly.graph_objs import Figure
import plotly.express as px


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
    fig.update_xaxes(title="RMSD (Å)", range=[0, 8])
    fig.update_yaxes(title="Frequency", range=[0, 1])
    return fig


def rename_legend_labels(newname_dict, fig):
    fig.for_each_trace(
        lambda t: t.update(
            name=newname_dict[t.name],
            legendgroup=newname_dict[t.name],
            hovertemplate=t.hovertemplate.replace(t.name, newname_dict[t.name]),
        )
    )
    return fig


def replace_xaxis_labels(fig: Figure, axis_title):
    fig.for_each_xaxis(lambda x: x.update(title=""))
    fig.add_annotation(
        x=0.5,
        y=-0.15,
        text=axis_title,
        textangle=0,
        font=dict(size=16),
        xref="paper",
        yref="paper",
        showarrow=False,
    )
    return fig


def replace_yaxis_labels(fig: Figure, axis_title):
    fig.for_each_yaxis(lambda y: y.update(title=""))
    fig.add_annotation(
        x=-0.05,
        y=0.5,
        text=axis_title,
        textangle=-90,
        font=dict(size=16),
        xref="paper",
        yref="paper",
        showarrow=False,
    )
    return fig


def clean_labels(fig):
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    return fig


def scatter_wrapper(
    df,
    kwarg_dict,
    x_axis_title=None,
    y_axis_title=None,
    replace_xaxis=False,
    replace_y_axis=False,
    clean=True,
    x_axis_reversed=False,
):
    fig: Figure = px.scatter(df, **kwarg_dict, hover_data=df.columns)
    if x_axis_title:
        if replace_xaxis:
            fig = replace_xaxis_labels(fig, x_axis_title)
        else:
            fig.update_xaxes(title=x_axis_title)

    if y_axis_title:
        if replace_y_axis:
            fig = replace_yaxis_labels(fig, y_axis_title)
        else:
            fig.update_yaxes(title=y_axis_title)

    if clean:
        fig = clean_labels(fig)
    if x_axis_reversed:
        fig.update_xaxes(autorange="reversed")
    return fig


import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score


def plot_scatter_with_regression_line_plotly(x, y):
    # Convert to numpy arrays
    x = np.array(x).reshape(-1, 1)
    y = np.array(y)

    # Fit the linear regression model
    model = LinearRegression()
    model.fit(x, y)

    # Predict y values using the fitted model
    y_pred = model.predict(x)

    # Calculate the R^2 value
    r2 = r2_score(y, y_pred)

    # Create the scatter plot
    scatter = go.Scatter(x=x.flatten(), y=y, mode="markers", name="Data points")

    # Create the regression line plot
    regression_line = go.Scatter(
        x=x.flatten(),
        y=y_pred,
        mode="lines",
        name=f"Regression line (R² = {r2:.2f})",
        line=dict(color="red"),
    )

    # Create the layout
    layout = go.Layout(
        title="Scatter Plot with Regression Line and R² Value",
        xaxis=dict(title="X"),
        yaxis=dict(title="Y"),
    )

    # Create the figure
    fig = go.Figure(data=[scatter, regression_line], layout=layout)

    # Show the plot
    return fig
