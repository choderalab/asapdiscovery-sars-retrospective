import pandas as pd
from typing import Dict, Any
import numpy as np
import plotly.graph_objects as go


def create_ecdf_figure(
    data: pd.DataFrame, x_column: str, color_column: str, layout_config: Dict[str, Any]
) -> go.Figure:
    """
    Create an ECDF figure based on the data and configuration.

    Args:
        data: DataFrame containing the data
        x_column: Column name for x-axis values
        color_column: Column name for grouping/coloring
        layout_config: Dictionary with Plotly layout configuration

    Returns:
        A Plotly figure object
    """
    # Get unique categories for grouping
    groups = data[color_column].unique()

    # Create figure
    fig = go.Figure()

    # Add an ECDF trace for each group
    for group in groups:
        # Filter data for this group
        group_data = data[data[color_column] == group][x_column]

        if len(group_data) == 0:
            continue

        # Sort the data and compute ECDF
        x = np.sort(group_data)
        y = np.arange(1, len(x) + 1) / len(x)

        # Add trace with any trace-specific config from YAML
        general_trace_props = {}
        if "traces" in layout_config:
            if "general" in layout_config["traces"]:
                general_trace_props = layout_config["traces"]["general"].copy()
            if "by_group" in layout_config["traces"]:
                general_trace_props.update(
                    layout_config["traces"]["by_group"][group].copy()
                )

        fig.add_trace(
            go.Scatter(x=x, y=y, mode="lines", name=group, **general_trace_props)
        )

    # Apply layout configuration from YAML
    if "layout" in layout_config:
        fig.update_layout(**layout_config["layout"])

    # Apply axis configurations if provided
    if "xaxis" in layout_config:
        fig.update_xaxes(**layout_config["xaxis"])

    if "yaxis" in layout_config:
        fig.update_yaxes(**layout_config["yaxis"])

    return fig
