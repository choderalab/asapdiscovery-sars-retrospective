import pytest
from data_schema import (
    PoseData,
    ChemicalSimilarityData,
    DockingDataModel,
    KeyColumn,
    ParamColumn,
    ValueColumn,
)
import pandas as pd
import numpy as np
import itertools


@pytest.fixture()
def refs():
    """Sample reference structures fixture."""
    return ["PDB123", "PDB456"]


@pytest.fixture()
def ligs():
    """Sample ligands fixture."""
    return ["LIG_A", "LIG_B", "LIG_C"]


@pytest.fixture()
def ref_dataframe(refs):
    """Sample reference data fixture."""
    return pd.DataFrame(
        {
            "Reference_Structure": refs,
            "Ref_Data_1": [np.random.random() for ref in refs],
        }
    )


@pytest.fixture()
def lig_dataframe(ligs):
    """Sample ligand data fixture."""
    return pd.DataFrame(
        {
            "Query_Ligand": ligs,
            "Lig_Data_1": [np.random.random() for lig in ligs],
        }
    )


@pytest.fixture()
def pose_dataframe(refs, ligs):
    """Sample pose results fixture."""
    return pd.DataFrame.from_records(
        [
            {
                "Reference_Structure": ref,
                "Query_Ligand": lig,
                "RMSD": np.random.random() * 8,
                "Pose_ID": pose,
            }
            for ref, lig, pose in itertools.product(refs, ligs, range(0, 2))
        ]
    )


@pytest.fixture()
def ecfp_dataframe(refs, ligs):
    """Sample ECFP data fixture."""
    return pd.DataFrame.from_records(
        [
            {
                "Reference_Structure": ref,
                "Query_Ligand": lig,
                "Tanimoto": np.random.random(),
                "Type": "ECFP",
                "radius": radius,
                "bitsize": bitsize,
            }
            for ref, lig, radius, bitsize in itertools.product(
                refs, ligs, [2, 5], [2048]
            )
        ]
    )


@pytest.fixture()
def tanimotocombo_data(refs, ligs):
    """Sample TanimotoCombo data fixture."""
    return pd.DataFrame.from_records(
        [
            {
                "Reference_Structure": ref,
                "Query_Ligand": lig,
                "Tanimoto": np.random.random(),
                "Aligned": aligned,
            }
            for ref, lig, aligned in itertools.product(refs, ligs, ["True", "False"])
        ]
    )


def test_pose_data_model(pose_dataframe):
    """Test the PoseData model."""
    pose_data = PoseData(
        dataframe=pose_dataframe,
    )
    pose_data.to_parquet("pose_data.parquet")

    # Load the DataFrame from the parquet file
    loaded_pose_data = PoseData.from_parquet("pose_data.parquet")

    assert pose_data == loaded_pose_data

    # Check that the loaded DataFrame matches the original
    pd.testing.assert_frame_equal(pose_dataframe, loaded_pose_data.dataframe)


def test_chemical_similarity_data_model(ecfp_dataframe, tanimotocombo_data):
    ecfp_data = ChemicalSimilarityData(
        dataframe=ecfp_dataframe,
        type=ParamColumn(name="ECFP"),
        other_columns=[
            ParamColumn(name="radius"),
            ParamColumn(name="bitsize"),
        ],
    )
    ecfp_data.to_parquet("ecfp_data.parquet")
    loaded_ecfp_data = ChemicalSimilarityData.from_parquet("ecfp_data.parquet")
    assert ecfp_data == loaded_ecfp_data
    pd.testing.assert_frame_equal(ecfp_dataframe, loaded_ecfp_data.dataframe)

    # Test TanimotoCombo data
    tanimotocombo_data = ChemicalSimilarityData(
        dataframe=tanimotocombo_data,
        type=ParamColumn(name="TanimotoCombo"),
        other_columns=[ParamColumn(name="Aligned")],
    )
    tanimotocombo_data.to_parquet("tanimotocombo_data.parquet")
    loaded_tanimotocombo_data = ChemicalSimilarityData.from_parquet(
        "tanimotocombo_data.parquet"
    )
    assert tanimotocombo_data == loaded_tanimotocombo_data
    pd.testing.assert_frame_equal(
        tanimotocombo_data.dataframe, loaded_tanimotocombo_data.dataframe
    )


def test_docking_data_model(pose_dataframe, ecfp_dataframe, tanimotocombo_data):
    """Test the DockingDataModel."""
    docking_data = DockingDataModel(
        pose_data=PoseData(dataframe=pose_dataframe),
    )


def test_raises_validation_error():
    """Test that the ChemicalSimilarityData model raises a validation error when the dataframe is missing required columns."""
    with pytest.raises(ValueError):
        ChemicalSimilarityData(
            dataframe=pd.DataFrame(),
            other_columns=[ParamColumn(name="Aligned")],
        )
