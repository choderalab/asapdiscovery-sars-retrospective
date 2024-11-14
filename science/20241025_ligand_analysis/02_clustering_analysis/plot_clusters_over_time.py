"""
The purpose of this script is to plot the clusters over time.
"""

import argparse
from pathlib import Path
import pandas as pd
import json
from datetime import datetime


def parse_args():
    parser = argparse.ArgumentParser(description="Plot cluster scaffolds")
    parser.add_argument("--input_csv", type=Path, help="Path to the input CSV file")
    parser.add_argument("--output_dir", type=Path, help="Path to the output directory")
    parser.add_argument(
        "--compound_data_csv", type=Path, help="Path to the compound data csv"
    )
    parser.add_argument(
        "--date_json",
        default="/Users/alexpayne/Scientific_Projects/asapdiscovery-sars-retrospective/science/20240403_multi_pose_docking_v2/20240430_analyze_cross_docking_results/20240503_inputs_analysis/date_dict.json",
        type=Path,
        help="Path to the date JSON file",
    )
    return parser.parse_args()


def date_processor(date_string):
    if type(date_string) == str and not date_string == "None":
        try:
            return datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return datetime.strptime(date_string, "%d/%m/%Y %H:%M")
    else:
        return None


def make_image(df):
    import plotly.express as px

    large_font = 24
    small_font = 18

    fig = px.ecdf(
        df,
        x="Date",
        color="cluster_id",
        ecdfnorm=None,
        template="simple_white",
        height=600,
        width=800,
    )
    # update legend title
    fig.update_layout(legend_title_text="<b> Bemis-Murcko Cluster </b>")
    fig.update_xaxes(title_text="<b> Date of Crystal Structure Collection </b>")
    fig.update_yaxes(title_text="<b> Cumulative Number of Structures </b>")

    update_layout_dict = dict(
        xaxis=dict(
            title_font=dict(size=large_font),
            color="black",
        ),
        yaxis=dict(
            # range=(0,1),
            title_font=dict(size=large_font),
            color="black",
        ),
    )

    # move legend to inside the plot
    fig.update_layout(
        legend=dict(yanchor="bottom", y=0.25, xanchor="right", x=1.1),
        **update_layout_dict,
    )

    return fig


def main():
    args = parse_args()

    input_csv = args.input_csv
    output_dir = args.output_dir
    compound_data_csv = args.compound_data_csv

    with open(args.date_json, "r") as f:
        date_dict = [
            {"Name": name, "Date": date_processor(date)}
            for name, date in json.load(f).items()
        ]
        date_df = pd.DataFrame.from_records(date_dict)

    compound_data = pd.read_csv(compound_data_csv)
    compound_data["structure_name"] = (
        "Mpro-" + compound_data["series"] + compound_data["number"].astype(str)
    )

    compound_data = compound_data.merge(
        date_df, left_on="structure_name", right_on="Name"
    )

    df = pd.read_csv(input_csv)

    df = df.merge(compound_data, on="compound_name", how="left")

    fig = make_image(df)

    cluster_type = df["cluster_type"].unique()[0]

    # save year month day as a single string
    date = datetime.today().strftime("%Y%m%d")
    fig.write_image(
        output_dir / f"{date}_{cluster_type}_cumulative_cluster_by_date.svg"
    )
    fig.write_image(
        output_dir / f"{date}_{cluster_type}_cumulative_cluster_by_date.png"
    )


if __name__ == "__main__":
    main()
