"""
Create combinations of calculations to run on a cross-docking dataset
"""

from argparse import ArgumentParser
from harbor.analysis.cross_docking import (
    Settings,
)
from harbor.analysis.utils import FileLogger
from pathlib import Path
import pandas as pd


def get_args():
    parser = ArgumentParser(
        description="Create combinations of calculations to run on a cross-docking dataset"
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to the input CSV file containing the cross-docking data. ",
    )
    parser.add_argument(
        "--settings",
        type=Path,
        nargs="+",
        required=False,
        help="Path to the settings yaml files. Will be generated with defaults if not provided.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Path to the output directory where the results will be stored",
        required=True,
    )
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

    if args.settings:
        logger.info(f"Reading {len(args.settings)} settings files")
        settings_list = [
            (settings.stem, Settings.from_yaml_file(settings))
            for settings in args.settings
        ]
    else:
        logger.info("No settings file provided, using defaults")
        settings_list = [("default", Settings())]

    logger.info(f"Reading from {args.input}")
    df = pd.read_csv(args.input, index_col=0)
    logger.info(f"Read {len(df)} rows")

    logger.info("Creating evaluators")
    for name, settings in settings_list:
        logger.info(f"Creating evaluators for settings {name}")
        evaluators = settings.create_evaluators(df, logger)
        logger.info(f"Made {len(evaluators)} evaluators")
        logger.info(f"Saving settings to {output_dir / f'{name}.yaml'}")
        settings.to_yaml_file(output_dir / f"{name}.yaml")

        logger.info(f"Saving evaluators to {output_dir}")
        for i, evaluator in enumerate(evaluators):
            evaluator.to_json_file(output_dir / f"evaluator_{name}_{i}.json")

        logger.info(f"Creating table summary for {name}")
        output_dataframe = pd.DataFrame.from_records(
            [ev.get_records() for ev in evaluators]
        )
        output_dataframe.to_csv(output_dir / f"summary_{name}.csv")


if __name__ == "__main__":
    main()
