"""
This script combines the results csvs and generates an input CSV that will be used to run the full cross docking evaluation.
"""

import pandas as pd
from pathlib import Path
from harbor.analysis.cross_docking import (
    DataFrameModel,
    DataFrameType,
    DockingDataModel,
)
import click


@click.command()
@click.argument("pose-data", type=click.Path(exists=True))
@click.option("--tc-data", type=click.Path(exists=True))
@click.option("--ecfp-data", type=click.Path(exists=True))
@click.option("--mcs-data", type=click.Path(exists=True))
@click.option("--scaffold-data", type=click.Path(exists=True))
@click.option("--deduplicate/--no-deduplicate", default=False)
@click.option("--output-file-prefix", required=True, help="Output file suffix")
def main(
    pose_data,
    tc_data,
    ecfp_data,
    mcs_data,
    scaffold_data,
    deduplicate,
    output_file_prefix,
):

    dfms = []

    pose_df = pd.read_csv(pose_data)

    pose_dfm = DataFrameModel(
        name="PoseData",
        type=DataFrameType.POSE,
        dataframe=pose_df,
        key_columns=[
            "Reference_Structure",
            "Query_Ligand",
            "Reference_Ligand",
            "Pose_ID",
        ],
    )

    dfms.extend([pose_dfm])

    common_key_cols = ["Reference_Ligand", "Query_Ligand"]

    def get_dataframe(
        df_path: Path,
        deduplicate: bool,
        param_args: list = [],
    ):
        return (
            pd.read_csv(df_path).groupby(common_key_cols + param_args).head(1)
            if deduplicate
            else pd.read_csv(df_path)
        )

    if tc_data:
        dfms.append(
            DataFrameModel(
                name="TanimotoComboData",
                type=DataFrameType.CHEMICAL_SIMILARITY,
                dataframe=get_dataframe(tc_data, deduplicate, ["Aligned"]),
                key_columns=common_key_cols,
                param_columns=["Aligned"],
            )
        )
    if ecfp_data:
        dfms.append(
            DataFrameModel(
                name="ECFPData",
                type=DataFrameType.CHEMICAL_SIMILARITY,
                dataframe=get_dataframe(ecfp_data, deduplicate, ["radius", "bitsize"]),
                key_columns=common_key_cols,
                param_columns=["radius", "bitsize"],
            )
        )
    if mcs_data:
        df = get_dataframe(mcs_data, deduplicate)
        dfms.append(
            DataFrameModel(
                name="MCSData",
                type=DataFrameType.CHEMICAL_SIMILARITY,
                dataframe=df,
                key_columns=common_key_cols,
            )
        )
    if scaffold_data:
        query_data = pd.read_csv(scaffold_data)
        query_data.columns = [
            "Query_Ligand",
            "Scaffold_ID",
            "Scaffold_Smarts",
            "Scaffold_Type",
        ]
        dfms.append(
            DataFrameModel(
                name="QueryData",
                type=DataFrameType.QUERY,
                dataframe=(
                    query_data.groupby("Query_Ligand").head(1)
                    if deduplicate
                    else query_data
                ),
                key_columns=["Query_Ligand"],
                param_columns=["Scaffold_Type"],
            )
        )

        ref_data = pd.read_csv(scaffold_data)
        ref_data.columns = [
            "Reference_Ligand",
            "Scaffold_ID",
            "Scaffold_Smarts",
            "Scaffold_Type",
        ]
        dfms.append(
            DataFrameModel(
                name="RefData",
                type=DataFrameType.REFERENCE,
                dataframe=(
                    ref_data.groupby("Reference_Ligand").head(1)
                    if deduplicate
                    else ref_data
                ),
                key_columns=["Reference_Ligand"],
                param_columns=["Scaffold_Type"],
            )
        )

    ddm = DockingDataModel.from_models(dfms)
    ddm.serialize(output_file_prefix)


if __name__ == "__main__":
    main()
