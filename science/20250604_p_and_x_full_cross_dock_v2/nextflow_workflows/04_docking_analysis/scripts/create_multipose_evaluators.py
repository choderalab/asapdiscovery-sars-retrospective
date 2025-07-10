"""
This script creates the calculations that will be run on a cross-docking dataset
"""

import click
from pathlib import Path
import pandas as pd
import harbor.analysis.cross_docking as cd


@click.command()
# @click.option(
#     "-i",
#     "--input-parquet",
#     required=True,
#     help="Path to input parquet file made by DockinDataModel",
#     type=click.Path(exists=True, path_type=Path),
# )
@click.option(
    "-o",
    "--output",
    type=Path,
    required=True,
    help="Path to the output directory where the results will be stored",
)
def main(output):
    # data = cd.DockingDataModel.deserialize(input_parquet)
    name = "multipose_evaluators"
    output = output / name
    output.mkdir(exist_ok=True, parents=True)

    ref_structure_column = "Reference_Structure"

    n_refs = cd.generate_logarithmic_scale(
        403,
    )
    n_poses = [1, 2, 5, 10, 25, 50]
    pose_selectors = [
        cd.PoseSelector(
            name="PoseSelector", variable="Pose_ID", ascending=True, number_to_return=n
        )
        for n in n_poses
    ]

    scorers = [
        cd.POSITScorer(variable="PoseData_docking-confidence-POSIT"),
        cd.RMSDScorer(variable="PoseData_RMSD", cutoff=2),
    ]
    dataset_splits = [
        cd.DateSplit(
            date_column="RefData_Date",
            randomize_by_n_days=1,
            reference_structure_column=ref_structure_column,
        ),
        cd.RandomSplit(
            reference_structure_column=ref_structure_column,
        ),
    ]

    evs = []
    for pose_selector in pose_selectors:
        for scorer in scorers:
            for dataset_split in dataset_splits:
                for n in n_refs:
                    ev = cd.Evaluator(
                        pose_selector=pose_selector,
                        scorer=scorer,
                        evaluator=cd.BinaryEvaluation(
                            variable="PoseData_RMSD", cutoff=2
                        ),
                        n_bootstraps=1000,
                    )
                    ev.dataset_split = dataset_split
                    ev.dataset_split.n_reference_structures = n
                    evs.append(ev)

    for i, evaluator in enumerate(evs):
        evaluator.to_json_file(output / f"evaluator_{name}_{i}.json")

    df = pd.DataFrame.from_records([ev.get_records() for ev in evs])
    df.to_csv(output / f"pose_split_evaluators.csv")


if __name__ == "__main__":
    main()
