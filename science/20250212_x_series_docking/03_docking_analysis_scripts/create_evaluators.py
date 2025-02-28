"""
Create combinations of calculations to run on a cross-docking dataset
"""

from argparse import ArgumentParser
from harbor.analysis.cross_docking import (
    Settings,
    Evaluator,
    PoseSelector,
    RandomSplit,
    DateSplit,
    Scorer,
    BinaryEvaluation,
    StructureChoice,
)
from harbor.analysis.utils import FileLogger
from pathlib import Path
import pandas as pd
import numpy as np


def get_args():
    parser = ArgumentParser(
        description="Create combinations of calculations to run on a cross-docking dataset"
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=False,
        help="Path to the input CSV file containing the cross-docking data. ",
    )
    parser.add_argument(
        "--settings",
        type=Path,
        required=False,
        help="Path to the settings yaml file. Will be generated with defaults if not provided.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Path to the output directory where the results will be stored",
        required=True,
    )
    parser.add_argument("--update-n-per-split", action="store_true")
    return parser.parse_args()


def main():
    args = get_args()
    args.output.mkdir(exist_ok=True, parents=True)
    output_dir = args.output
    logger = FileLogger(
        logname="create_evaluators",
        path=output_dir,
        logfile="create_evaluators.log",
    ).getLogger()

    if args.update_n_per_split:
        if not args.input:
            raise ValueError("Must provide input file to update n_per_split")

    logger.info("Reading input data")
    if args.input:
        logger.info(f"Reading from {args.input}")
        df = pd.read_csv(args.input, index_col=0)

    if args.settings:
        logger.info(f"Reading settings from {args.settings}")
        settings = Settings.from_yml_file(args.settings)
    else:
        logger.info("No settings file provided, using defaults")
        settings = Settings()

    if args.update_n_per_split:
        logger.info("Updating n_per_split")
        n_per_split = np.arange(1, 21)
        n_per_split = np.concatenate(
            (n_per_split, np.arange(25, len(df.Reference_Structure.unique()), 20))
        )
        settings.n_per_split = n_per_split

    logger.info("Writing settings to disk")
    settings.to_yml_file(output_dir / "settings.yml")

    logger.info("Creating pose selectors")
    pose_selectors = [
        PoseSelector(
            name="Default", variable=settings.pose_id_column, number_to_return=n
        )
        for n in settings.n_poses
    ]

    logger.info("Setting up dataset splits")
    dataset_splits = []
    if settings.use_random_split:
        dataset_splits.extend(
            [
                RandomSplit(
                    variable=settings.reference_ligand_column,
                    n_splits=1,
                    n_per_split=n_per_split,
                )
                for n_per_split in settings.n_per_split
            ]
        )
    if settings.use_date_split:
        if not args.input:
            raise ValueError("Must provide input file to use date split")
        logger.info("Loading date information")
        date_dict_list = df.groupby(settings.reference_structure_column)[
            [
                settings.reference_structure_column,
                settings.reference_structure_date_column,
            ]
        ].to_dict(orient="records")

        simplified_date_dict = {
            date_dict[settings.reference_structure_column]: date_dict[
                settings.reference_structure_date_column
            ]
            for date_dict in date_dict_list
        }
        dataset_splits.extend(
            [
                DateSplit(
                    variable=settings.reference_structure_column,
                    n_per_split=n_per_split,
                    balanced=True,  # haven't implemented this otherwise
                    date_dict=simplified_date_dict,
                    randomize_by_n_days=settings.randomize_by_n_days,
                )
                for n_per_split in settings.n_per_split
            ]
        )

        logger.info("Adding scorers")
        scorers = []
        if settings.use_posit_scorer:
            scorers.extend(
                Scorer(
                    name=settings.posit_name,
                    variable=settings.posit_score_column_name,
                    higher_is_better=True,
                    number_to_return=1,
                )
            )
        if settings.use_rmsd_scorer:
            scorers.extend(
                Scorer(
                    name=settings.rmsd_name,
                    variable=settings.rmsd_column_name,
                    higher_is_better=False,
                    number_to_return=1,
                )
            )
        rmsd_evaluator = BinaryEvaluation(
            variable=settings.rmsd_column_name, cutoff=settings.rmsd_cutoff
        )

        logger.info("Creating evaluators")
        evaluators = []
        for pose_selector in pose_selectors:
            for dataset_split in dataset_splits:
                for scorer in scorers:
                    evaluator = Evaluator(
                        pose_selector=pose_selector,
                        dataset_split=dataset_split,
                        scorer=scorer,
                        evaluator=rmsd_evaluator,
                        groupby=[settings.query_ligand_column],
                        n_bootstraps=settings.n_bootstraps,
                    )
                    evaluators.append(evaluator)

        logger.info(f"Made {len(evaluators)} evaluators")
        logger.info("Writing evaluators to disk")
        for i, evaluator in enumerate(evaluators):
            evaluator.to_json_file(output_dir / f"evaluator_{i}.json")


if __name__ == "__main__":
    main()
