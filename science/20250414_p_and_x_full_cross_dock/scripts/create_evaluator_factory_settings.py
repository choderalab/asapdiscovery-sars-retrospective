"""
This script creates the settings files used to create the analysis
"""

import click
from pathlib import Path
from harbor.analysis.cross_docking import (
    EvaluatorFactory,
    ScaffoldSplitOptions,
)


@click.command()
@click.option(
    "-o",
    "--output",
    type=Path,
    required=False,
    default="./",
    help="Path to the output directory where the results will be stored",
)
def main(output):
    output.mkdir(exist_ok=True, parents=True)

    # update default settings
    default = EvaluatorFactory(name="default")
    default.scorer_settings.rmsd_scorer_settings.use = True
    default.scorer_settings.posit_scorer_settings.use = True

    # basic date split cross docking
    evf = default.__deepcopy__()
    evf.name = "reference_split_comparison"
    evf.reference_split_settings.use = True
    evf.reference_split_settings.date_split_settings.use = True
    evf.reference_split_settings.date_split_settings.reference_structure_date_column = (
        "Reference_Structure_Date"
    )
    evf.reference_split_settings.random_split_settings.use = True
    evf.reference_split_settings.update_reference_settings.use = True
    evf.reference_split_settings.update_reference_settings.use_logarithmic_scaling = (
        True
    )
    evf.to_yaml_file(output)

    # Scaffold split options
    default_scaffold = default.__deepcopy__()
    default_scaffold.name = "default_scaffold_settings"
    default_scaffold.pairwise_split_settings.use = True
    default_scaffold.pairwise_split_settings.scaffold_split_settings.use = True
    default_scaffold.pairwise_split_settings.scaffold_split_settings.reference_scaffold_min_count = (
        5
    )
    default_scaffold.pairwise_split_settings.scaffold_split_settings.query_scaffold_min_count = (
        5
    )

    # x_to_x default
    x_to_x_default = default_scaffold.__deepcopy__()
    x_to_x_default.name = "x_to_x_scaffold_split"
    x_to_x_default.pairwise_split_settings.scaffold_split_settings.scaffold_split_option = (
        ScaffoldSplitOptions.X_TO_X
    )
    x_to_x_default.to_yaml_file(output)

    # x_to_y default
    x_to_y_default = default_scaffold.__deepcopy__()
    x_to_y_default.name = "x_to_y_scaffold_split"
    x_to_y_default.pairwise_split_settings.scaffold_split_settings.scaffold_split_option = (
        ScaffoldSplitOptions.X_TO_Y
    )
    x_to_y_default.to_yaml_file(output)

    # x to y scaffold split with 10 refs
    evf = x_to_y_default.__deepcopy__()
    evf.name = "x_to_y_scaffold_split_10_refs"
    evf.combine_reference_and_similarity_splits = True
    evf.reference_split_settings.random_split_settings.use = True
    evf.reference_split_settings.n_reference_structures = [5]
    evf.to_yaml_file(output)


if __name__ == "__main__":
    main()
