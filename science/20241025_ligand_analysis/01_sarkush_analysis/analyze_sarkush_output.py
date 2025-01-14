"""
This script tries to generate a useful output from the SARKush data.
"""

import argparse
from pathlib import Path
import pandas as pd
import json


def parse_args():
    parser = argparse.ArgumentParser(description="Analyze SARKush output")
    parser.add_argument("--input_dir", type=Path, help="Path to the input directory")
    parser.add_argument("--output_dir", type=Path, help="Path to the output directory")
    return parser.parse_args()


def main():
    args = parse_args()
    input_dir = args.input_dir
    output_dir = args.output_dir

    with open(input_dir / "task_messages.txt") as f:
        report_data = [line.rstrip().split("\t") for line in f.readlines()]
        report_data = {
            data[0]: data[1] if len(data) > 1 else "None" for data in report_data
        }

    job_id = report_data["job_ID"]

    output_dfs = []
    csv_files = list(input_dir.glob("*decomposition_data.csv"))
    for csv_file in csv_files:
        sarkush_id = csv_file.stem.split("_")[1]
        df = pd.read_csv(csv_file)
        output_dfs.append(
            pd.DataFrame(
                {
                    "compound_name": df["compound_name"],
                    "cluster_id": sarkush_id,
                    "scaffold_smarts": df["SARkush_smiles"],
                    "cluster_type": f"sarkush_{job_id}",
                }
            )
        )
    output_df = pd.concat(output_dfs)

    # Get Max Sarkush ID
    max_sarkush_id = int(output_df["cluster_id"].max())
    singleton_df = pd.read_csv(input_dir / f"Singletons.csv")
    new_singleton_df = pd.DataFrame(
        {
            "compound_name": singleton_df["compound_name"],
            "cluster_id": range(
                max_sarkush_id + 1, max_sarkush_id + 1 + len(singleton_df)
            ),
            "scaffold_smarts": singleton_df["compound_structure"],
            "cluster_type": f"sarkush_{job_id}",
        }
    )
    output_df = pd.concat([output_df, new_singleton_df])

    with open(output_dir / f"{job_id}_report_data.json", "w") as f:
        json.dump(report_data, f)

    output_df.to_csv(output_dir / f"{job_id}_sarkush_output.csv", index=False)


if __name__ == "__main__":
    main()
