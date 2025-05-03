"""
This script creates the calculations that will be run on a cross-docking dataset
"""

import click
from pathlib import Path
from harbor.analysis.cross_docking import DockingDataModel, EvaluatorFactory
from harbor.analysis.utils import FileLogger


@click.command()
@click.option(
    "-i",
    "--input-parquet",
    required=True,
    help="Path to input parquet file made by DockinDataModel",
    type=click.Path(exists=True, path_type=Path),
)
@click.option(
    "-o",
    "--output",
    type=Path,
    required=True,
    help="Path to the output directory where the results will be stored",
)
def main(input_parquet, output):
    output.mkdir(exist_ok=True, parents=True)

    logger = FileLogger(
        logname="create_evaluators", path=output, logfile="create_evaluators.log"
    ).getLogger()
    logger.info(f"Reading data model from {input_parquet}")
    # load docking model
    data = DockingDataModel.deserialize(input_parquet)

    evf = EvaluatorFactory()
    evf.to_yaml_file(output / "default.yaml")

    # basic date split cross docking
    name = "reference_split_comparison"
    evf.reference_split_settings.use = True
    evf.reference_split_settings.date_split_settings.use = True
    evf.reference_split_settings.date_split_settings.reference_structure_date_column = (
        "Reference_Structure_Date"
    )
    evf.reference_split_settings.random_split_settings.use = True
    evf.scorer_settings.rmsd_scorer_settings.use = True
    evf.scorer_settings.posit_scorer_settings.use = True

    evf.reference_split_settings.update_reference_settings.use = True
    evf.reference_split_settings.update_reference_settings.use_logarithmic_scaling = (
        True
    )
    evf.to_yaml_file(output / f"{name}.yaml")

    evs = evf.create_evaluators(data)
    logger.info(f"created {len(evs)} for {name}")
    for i, evaluator in enumerate(evs):
        evaluator.to_json_file(output / f"evaluator_{name}_{i}.json")


if __name__ == "__main__":
    main()
