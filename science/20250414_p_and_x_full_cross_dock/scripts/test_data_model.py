import pytest
from datetime import datetime, timedelta
import warnings
from harbor.analysis.cd2 import (
    PoseData,
    ChemicalSimilarityData,
    ReferenceData,
    QueryData,
    DockingDataModel,
    ColumnType,
    KeyColumn,
    ParamColumn,
    ValueColumn,
    InfoColumn,
    ColumnFilter,
    ColumnSortFilter,
    DataFrameType,
    RandomSplit,
    DateSplit,
    ScaffoldSplitOptions,
    ScaffoldSplit,
    PoseSelector,
    Evaluator,
    POSITScorer,
    RMSDScorer,
    BinaryEvaluation,
    SuccessRate,
)
import pandas as pd
import numpy as np
import itertools


@pytest.fixture(autouse=True)
def setup_random_state():
    """Ensure consistent random state for all tests."""
    np.random.seed(42)
    yield
    np.random.seed(None)  # Reset the random state after each test


@pytest.fixture()
def refs():
    """Sample reference structures fixture."""
    return [f"PDB{i}" for i in range(1, 500)]


@pytest.fixture()
def ligs():
    """Sample ligands fixture."""
    return [f"LIG_{i}" for i in range(1, 500)]


@pytest.fixture()
def ref_dataframe(refs):
    """Sample reference data fixture."""
    return pd.DataFrame(
        {
            "Reference_Structure": refs,
            "Ref_Data_1": [np.random.random() for ref in refs],
            "Date": [datetime.now() - timedelta(days=i) for i in range(len(refs))],
            "Ref_Scaffold": [
                np.random.choice(["Scaffold1", "Scaffold2"]) for _ in refs
            ],
        }
    )


@pytest.fixture()
def lig_dataframe(ligs):
    """Sample ligand data fixture."""
    return pd.DataFrame(
        {
            "Query_Ligand": ligs,
            "Lig_Data_1": [np.random.random() for lig in ligs],
            "Query_Scaffold": [
                np.random.choice(["Scaffold1", "Scaffold2"]) for _ in ligs
            ],
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


@pytest.fixture()
def scaffold_dataframe(refs, ligs, ref_dataframe, lig_dataframe):
    """Sample scaffold data fixture."""
    return pd.DataFrame.from_records(
        [
            {
                "Reference_Structure": ref,
                "Query_Ligand": lig,
                "Tanimoto": (
                    1
                    if ref_dataframe[ref_dataframe["Reference_Structure"] == ref][
                        "Ref_Scaffold"
                    ].values[0]
                    == lig_dataframe[lig_dataframe["Query_Ligand"] == lig][
                        "Query_Scaffold"
                    ].values[0]
                    else 0
                ),
            }
            for ref, lig in itertools.product(refs, ligs)
        ]
    )


def test_column_filter(pose_dataframe):
    """Test the ColumnFilter class."""

    cf = ColumnFilter(
        column=ValueColumn(name="RMSD"),
        value=4.0,
        operator="le",
        data_type=DataFrameType.POSE,
    )
    filtered_df = cf.filter(pose_dataframe)
    assert len(filtered_df) == 28  # 2 poses per reference-ligand pair
    assert all(filtered_df["RMSD"] <= 4.0)

    # Test with a different operator
    cf = ColumnFilter(
        column=ValueColumn(name="RMSD"),
        value=4.0,
        operator="ge",
        data_type=DataFrameType.POSE,
    )
    filtered_df = cf.filter(pose_dataframe)
    assert len(filtered_df) == 26
    assert all(filtered_df["RMSD"] >= 4.0)


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
        name=InfoColumn(name="ECFP"),
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
        name=InfoColumn(name="TanimotoCombo"),
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


@pytest.fixture()
def docking_data_model(
    ref_dataframe,
    lig_dataframe,
    pose_dataframe,
    ecfp_dataframe,
    tanimotocombo_data,
    scaffold_dataframe,
):
    """Fixture for DockingDataModel."""
    return DockingDataModel(
        evaluation_key_columns=[KeyColumn(name="Query_Ligand")],
        pose_data=PoseData(dataframe=pose_dataframe),
        reference_data=ReferenceData(
            dataframe=ref_dataframe,
            other_columns=[
                ValueColumn(name="Ref_Data_1"),
                ValueColumn(name="Date"),
                ValueColumn(name="Ref_Scaffold"),
            ],
        ),
        query_data=QueryData(
            dataframe=lig_dataframe,
            other_columns=[
                ValueColumn(name="Lig_Data_1"),
                ValueColumn(name="Query_Scaffold"),
            ],
        ),
        chemical_similarity_data=[
            ChemicalSimilarityData(
                dataframe=ecfp_dataframe,
                name=InfoColumn(name="ECFP"),
                other_columns=[
                    ParamColumn(name="radius"),
                    ParamColumn(name="bitsize"),
                ],
            ),
            ChemicalSimilarityData(
                dataframe=tanimotocombo_data,
                name=InfoColumn(name="TanimotoCombo"),
                other_columns=[ParamColumn(name="Aligned")],
            ),
            ChemicalSimilarityData(
                dataframe=scaffold_dataframe,
                name=InfoColumn(name="ScaffoldMatch"),
            ),
        ],
    )


def test_docking_data_model(
    docking_data_model,
    ref_dataframe,
    lig_dataframe,
    pose_dataframe,
    ecfp_dataframe,
    tanimotocombo_data,
):
    """Test the DockingDataModel."""
    docking_data = docking_data_model.copy()

    # Check that the dataframes are combined correctly
    combined_df = docking_data.get_combined_dataframe()
    assert combined_df.size == 3510

    # Check that the combined DataFrame has the expected columns
    expected_columns = [
        "Reference_Structure",
        "Query_Ligand",
        "RMSD",
        "Pose_ID",
        "Tanimoto",
        "radius",
        "bitsize",
        "Aligned",
    ]
    assert all(col in combined_df.columns for col in expected_columns)

    # Check filtering
    cf1 = ColumnFilter(
        column=ValueColumn(name="RMSD"),
        value=2.0,
        operator="le",
        data_type=DataFrameType.POSE,
    )
    cf2 = ColumnFilter(
        column=KeyColumn(name="Reference_Structure"),
        value="PDB7",
        operator="eq",
        data_type=DataFrameType.REFERENCE,
    )
    filtered_data = docking_data.apply_filters([cf1, cf2])
    filtered_df = filtered_data.get_combined_dataframe()
    assert filtered_df["Reference_Structure"].nunique() == 1
    assert all(filtered_df["RMSD"] <= 2.0)


def test_new_splits(docking_data_model):
    """Test the RandomSplit class."""
    random_split = RandomSplit(
        n_reference_structures=3,
        reference_structure_column="Reference_Structure",
    )
    splits = random_split.run(docking_data_model, bootstraps=10)

    assert len(splits) == 10

    # make sure the splits are not all the same
    assert len(set([tuple(split.get_unique_refs()) for split in splits])) > 1

    # make sure the splits have the right number of structures
    assert all(len(split.get_unique_refs()) == 3 for split in splits)

    date_split = DateSplit(
        n_reference_structures=3,
        reference_structure_column="Reference_Structure",
        date_column="Date",
        randomize_by_n_days=3,
    )
    splits = date_split.run(docking_data_model, bootstraps=10)
    assert len(splits) == 10

    # make sure the splits are not all the same
    assert len(set([tuple(split.get_unique_refs()) for split in splits])) > 1

    # make sure the splits have the right number of structures
    assert all(len(split.get_unique_refs()) == 3 for split in splits)


def test_scaffold_split(docking_data_model):
    """Test the ScaffoldSplit class."""
    data_copy = docking_data_model.copy()
    split_options = [
        (ScaffoldSplitOptions.X_TO_Y, "Scaffold1", "Scaffold2"),
        (ScaffoldSplitOptions.X_TO_NOT_X, "Scaffold1", None),
        (ScaffoldSplitOptions.NOT_X_TO_X, None, "Scaffold1"),
        (ScaffoldSplitOptions.X_TO_ALL, "Scaffold2", None),
        (ScaffoldSplitOptions.ALL_TO_X, None, "Scaffold2"),
    ]
    for split_option, query_subset, ref_subset in split_options:
        scaffold_split = ScaffoldSplit(
            query_scaffold_id_column="Query_Scaffold",
            reference_scaffold_id_column="Ref_Scaffold",
            split_option=split_option,
            reference_scaffold_id_subset=[ref_subset] if ref_subset else None,
            query_scaffold_id_subset=[query_subset] if query_subset else None,
        )
        splits = scaffold_split.run(data_copy)

        assert len(splits) == 1
        split_data = splits[0]

        combined_df = split_data.get_combined_dataframe()

        # check that the ref and query scaffolds are the only ones included
        if ref_subset:
            assert all(
                combined_df["Ref_Scaffold"].isin([ref_subset])
            ), f"Ref_Scaffold should only contain {ref_subset}"
        if query_subset:
            assert all(
                combined_df["Query_Scaffold"].isin([query_subset])
            ), f"Query_Scaffold should only contain {query_subset}"

        if split_option in (
            ScaffoldSplitOptions.X_TO_Y,
            ScaffoldSplitOptions.X_TO_NOT_X,
            ScaffoldSplitOptions.NOT_X_TO_X,
        ):
            # None of the scaffolds should match
            assert (
                len(
                    combined_df[
                        combined_df["Query_Scaffold"] == combined_df["Ref_Scaffold"]
                    ]
                )
                == 0
            )
        elif split_option in ScaffoldSplitOptions.X_TO_ALL:
            # should have the same refs as before
            assert data_copy.get_unique_refs() == split_data.get_unique_refs()
        elif split_option in ScaffoldSplitOptions.ALL_TO_X:
            # should have the same ligs as before
            assert data_copy.get_unique_ligs() == split_data.get_unique_ligs()


def test_n_structures_too_high(docking_data_model):
    """Test that all the splits are the same when n_per_split is too high."""
    with pytest.raises(ValueError):
        RandomSplit(
            n_reference_structures=1000,
            reference_structure_column="Reference_Structure",
        ).run(docking_data_model, bootstraps=10)

    splits = RandomSplit(
        reference_structure_column="Reference_Structure",
    ).run(docking_data_model, bootstraps=10)
    assert len(splits) == 10
    # all these splits should be the same
    assert len(set([tuple(split.get_unique_refs()) for split in splits])) == 1

    with pytest.raises(ValueError):
        DateSplit(
            n_reference_structures=1000,
            reference_structure_column="Reference_Structure",
            date_column="Date",
        ).run(docking_data_model, bootstraps=10)

    splits = DateSplit(
        reference_structure_column="Reference_Structure",
        date_column="Date",
    ).run(docking_data_model, bootstraps=10)
    assert len(splits) == 10
    # all these splits should be the same
    assert len(set([tuple(split.get_unique_refs()) for split in splits])) == 1


def test_sortfilter(docking_data_model):
    """Test the ColumnSortFilter class."""
    key_columns = docking_data_model.pose_data.get_columns(column_type=ColumnType.KEY)
    sf = ColumnSortFilter(
        data_type=DataFrameType.POSE,
        sort_column=KeyColumn(name="Pose_ID"),
        key_columns=key_columns,
    )

    new_data = docking_data_model.apply_filters([sf])
    new_combined_df = new_data.get_combined_dataframe()
    assert all(new_combined_df["Pose_ID"] == 0)


def test_pose_selector(docking_data_model):
    pose_selector = PoseSelector(name="Default", variable="Pose_ID", number_to_return=1)
    new_data = pose_selector.run(docking_data_model)
    assert all(new_data.get_combined_dataframe()["Pose_ID"] == 0)


def test_evaluator(docking_data_model):
    data = docking_data_model.copy()
    ev = Evaluator(
        dataset_split=RandomSplit(
            reference_structure_column="Reference_Structure", n_reference_structures=5
        ),
        scorer=RMSDScorer(),
        evaluator=BinaryEvaluation(variable="RMSD", cutoff=2),
        n_bootstraps=100,
    )
    df = docking_data_model.get_combined_dataframe()
    total = len(df.groupby([ky.name for ky in data.evaluation_key_columns]))
    filtered = df[df["RMSD"] < 2]
    filtered = filtered.groupby("Query_Ligand").head(1)
    fraction = filtered["RMSD"].apply(lambda x: x <= 2).sum() / total

    success_rate = ev.run(docking_data_model)
    assert isinstance(success_rate, SuccessRate)
    assert np.isclose(success_rate.fraction, fraction)


def test_performance(docking_data_model):
    from harbor.analysis import cross_docking as cd

    df = docking_data_model.get_combined_dataframe()

    old_ev = cd.Evaluator(
        pose_selector=cd.PoseSelector(
            name="Default",
            variable="Pose_ID",
            groupby=["Query_Ligand", "Reference_Structure"],
        ),
        dataset_split=cd.RandomSplit(
            n_per_split=5, reference_structure_column="Reference_Structure"
        ),
        scorer=cd.RMSDScorer(),
        evaluator=cd.BinaryEvaluation(variable="RMSD", cutoff=2),
        groupby=["Query_Ligand"],
        n_bootstraps=100,
    )

    new_ev = Evaluator(
        dataset_split=RandomSplit(
            reference_structure_column="Reference_Structure", n_reference_structures=5
        ),
        scorer=RMSDScorer(),
        evaluator=BinaryEvaluation(variable="RMSD", cutoff=2),
        n_bootstraps=100,
    )

    # compare time
    import time

    # Time old evaluator
    start_time = time.perf_counter()
    old_results = old_ev.run(df)
    old_time = time.perf_counter() - start_time

    # Time new evaluator
    start_time = time.perf_counter()
    new_results = new_ev.run(docking_data_model)
    new_time = time.perf_counter() - start_time

    print(f"\nPerformance comparison:")
    print(f"Old evaluator: {old_time:.3f} seconds")
    print(f"New evaluator: {new_time:.3f} seconds")
    print(f"Speedup: {old_time / new_time:.2f}x")
    print(old_results)
    print(new_results)


def test_raises_validation_error():
    """Test that the ChemicalSimilarityData model raises a validation error when the dataframe is missing required columns."""
    with pytest.raises(ValueError):
        ChemicalSimilarityData(
            dataframe=pd.DataFrame(),
            other_columns=[ParamColumn(name="Aligned")],
        )
