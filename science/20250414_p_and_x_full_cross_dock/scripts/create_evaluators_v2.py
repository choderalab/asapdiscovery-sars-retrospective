"""
This script creates the calculations that will be run on a cross-docking dataset
"""

import click
from pathlib import Path
from harbor.analysis.cross_docking import (
    DockingDataModel,
    EvaluatorFactory,
    ScaffoldSplitOptions,
)
from harbor.analysis.utils import FileLogger


def save_and_create_evs(
    evf: EvaluatorFactory, data: DockingDataModel, name: str, output: Path, logger
):
    evf.to_yaml_file(output / f"{name}.yaml")
    evs = evf.create_evaluators(data)
    logger.info(f"created {len(evs)} for {name}")
    for i, evaluator in enumerate(evs):
        evaluator.to_json_file(output / f"evaluator_{name}_{i}.json")


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
    save_and_create_evs(evf, data, name, output, logger)

    # x to y scaffold split
    evf = EvaluatorFactory()
    name = "x_to_y_scaffold_split"
    evf.pairwise_split_settings.use = True
    evf.pairwise_split_settings.scaffold_split_settings.use = True
    evf.pairwise_split_settings.scaffold_split_settings.reference_scaffold_min_count = 5
    evf.pairwise_split_settings.scaffold_split_settings.query_scaffold_min_count = 5
    evf.pairwise_split_settings.scaffold_split_settings.scaffold_split_option = (
        ScaffoldSplitOptions.X_TO_Y
    )
    evf.scorer_settings.rmsd_scorer_settings.use = True
    evf.scorer_settings.posit_scorer_settings.use = True
    save_and_create_evs(evf, data, name, output, logger)

    # x to y scaffold split with 5 refs
    evf = EvaluatorFactory()
    name = "x_to_y_scaffold_split_5_refs"
    evf.pairwise_split_settings.use = True
    evf.pairwise_split_settings.scaffold_split_settings.use = True
    evf.pairwise_split_settings.scaffold_split_settings.reference_scaffold_min_count = (
        10
    )
    evf.pairwise_split_settings.scaffold_split_settings.query_scaffold_min_count = 10
    evf.pairwise_split_settings.scaffold_split_settings.scaffold_split_option = (
        ScaffoldSplitOptions.X_TO_Y
    )
    evf.scorer_settings.rmsd_scorer_settings.use = True
    evf.scorer_settings.posit_scorer_settings.use = True
    evf.combine_reference_and_similarity_splits = True
    evf.reference_split_settings.random_split_settings.use = True
    evf.reference_split_settings.n_reference_structures = [5]
    save_and_create_evs(evf, data, name, output, logger)


if __name__ == "__main__":
    main()
