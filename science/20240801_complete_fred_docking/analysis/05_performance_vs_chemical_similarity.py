import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from pathlib import Path
import harbor.analysis.cross_docking as cd
import argparse
import multiprocessing as mp


def get_args():
    parser = argparse.ArgumentParser(
        description="Generate performance vs chemical similarity plots"
    )
    parser.add_argument(
        "-i",
        "--input_file",
        type=Path,
        required=True,
        help="Path to input file",
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        type=Path,
        required=True,
        help="Path to output directory",
    )
    return parser.parse_args()


def calculate_sectioned_performance(df, tc_cutoffs, bootstraps=1000):
    results_dicts = []
    for scorer_fxn, ascending in zip(
        ["docking-confidence-POSIT", "RMSD"], [False, True]
    ):
        for lower, upper in zip(tc_cutoffs[:-1], tc_cutoffs[1:]):
            new_df = df[(df.Tanimoto > lower) & (df.Tanimoto <= upper)]

            for i in range(bootstraps):
                if i != 0:
                    new_df = new_df.groupby("Query_Ligand").sample(frac=1, replace=True)
                new_df = new_df.sort_values(scorer_fxn, ascending=ascending)
                chosen_poses = new_df.groupby(["Query_Ligand"]).head(1)
                out_dict = {
                    "Tanimoto_Lower": lower,
                    "Tanimoto_Upper": upper,
                    "Total": 0,
                    "Fraction": 0,
                    "Dataset_Size": 0,
                    "Scorer": scorer_fxn,
                }
                if len(chosen_poses) != 0:
                    evaluator = cd.BinaryEvaluation(
                        variable="RMSD", cutoff=2.0, below_cutoff_is_good=True
                    )
                    fg = evaluator.run(chosen_poses, groupby="Query_Ligand")
                    out_dict.update(
                        {
                            "Total": fg.total,
                            "Fraction": fg.fraction,
                            "Dataset_Size": len(new_df),
                        }
                    )
                    out_dict.update(chosen_poses.POSIT_Method.value_counts().to_dict())
                results_dicts.append(out_dict)
    return pd.DataFrame.from_records(results_dicts)


def main():
    df =
    single_pose = results_df[results_df.Pose_ID == 0]


if __name__ == "__main__":
    main()
