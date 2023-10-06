import pandas as pd
from typing import Union


def get_df_subset(
    df,
    cutoff_column,
    cutoff,
    sort_column,
    ascending: bool = True,
    n: int = 1,
    selection_cols=("Compound_ID", "Version"),
):
    """
    Returns a subset of a DataFrame based on specified criteria.

    Parameters
    ----------
    df : pandas.DataFrame
        The input DataFrame containing the data to be filtered.
    cutoff_column : str
        The name of the column used for filtering the data.
    cutoff : int or float
        The cutoff value used for filtering the data. Rows where the value in `filter_column` is less than or equal to
        this cutoff will be included in the output.
    sort_column : str
        The name of the column used for sorting the data.
    ascending : bool, optional
        Whether to sort the data in ascending or descending order. The default value is True.
    n : int, optional
        The maximum number of rows to include in the output for each unique combination of values in `selection_cols`.
    selection_cols : tuple of str, optional
        The names of the columns to use for grouping and selecting rows. The default value is ("Compound_ID", "Version").

    Returns
    -------
    pandas.DataFrame
        A subset of the input DataFrame that meets the specified criteria, sorted by the `sort_column` and limited to
        `n` rows per unique combination of values in `selection_cols`.

    Examples
    --------
    >>> data = {
    ...     "Compound_ID": [1, 2, 3, 1, 2, 3, 1, 2, 3],
    ...     "Version": [1,1,1,2,2,2,2,2,2,],
    ...     "TanimotoCombo": [0.5,1,2, 0.5, 1,2, 0.5, 1, 2],
    ...     "RMSD": [1,1,1,1,1,1,2,2,2]
    ... }
    >>> df = pd.DataFrame(data)
    >>> get_df_subset(df, "TanimotoCombo", 1, "RMSD", 1, selection_cols=["Compound_ID", "Version"])
       Compound_ID  Version  TanimotoCombo  RMSD
    0            1        1            0.5     1
    1            2        1            1.0     1
    3            1        2            0.5     1
    4            2        2            1.0     1
    """
    return (
        df[df[cutoff_column] <= cutoff]
        .sort_values(sort_column, ascending=ascending)
        .groupby(list(selection_cols))
        .head(n)
    )


def calc_perc_good(
    df: pd.DataFrame,
    score_column: str,
    good_score: Union[int, float],
    total_mol: Union[pd.Series, int, float],
    split_cols: list[str] = None,
):
    """
    Calculates the percentage of 'good' scores in a DataFrame, relative to a specified threshold.

    Parameters
    ----------
    df : pandas.DataFrame
        The input DataFrame containing the data to be analyzed.
    score_column : str
        The name of the column containing the scores to be evaluated.
    good_score : int or float
        The threshold value used to define what is considered a 'good' score.
    total_mol : pandas.Series, int or float
        The total number of molecules or samples used as the denominator in the percentage calculation.
    split_cols : list[str], optional
        The names of the columns used to group the data. The default value is ["Version"].

    Returns
    -------
    pandas.Series
        A series containing the percentage of 'good' scores for each unique combination of values in `split_cols`.

    Examples
    --------
    >>> data = {
    ...     "Version": [1, 1, 2, 2, 2, 2],
    ...     "Method": ["Bad", "Good", "Bad", "Good", "Bad", "Good"],
    ...     "Score": [5, 1.9,5,1,2,2],
    ... }
    >>> df = pd.DataFrame(data)
    >>> calc_perc_good(df, "Score", 2, total_mol=df.groupby("Version")["Score"].nunique(), split_cols=["Version", "Method"])
    Version  Method
    1        Bad       0.000000
             Good      0.500000
    2        Bad       0.333333
             Good      0.666667
    Name: Score, dtype: float64
    """
    if split_cols is None:
        split_cols = ["Version"]
    group = df.groupby(split_cols, group_keys=True)
    return (
        group[score_column].apply(lambda x: x <= good_score).groupby(split_cols).sum()
        / total_mol
    )


def calculate_rmsd_stats(
    df: pd.DataFrame,
    query_mol_id: str,  # Column name of the molecule ID
    reference_selection: str,
    score_column: str,
    group_by: [str],
    ref_structure_stride: int = 10,
    ref_structure_id: str = "Structure_Name",
    n_bootstraps: int = 3,
    fraction_structures_used: float = 1.0,
    rmsd_col="RMSD",
    rmsd_cutoff: float = 2.0,
):
    dfs = []
    for i in range(n_bootstraps):

        # Randomize the order of the structures
        randomized = df.sample(frac=1)

        for n_ref in range(
            1, len(randomized[ref_structure_id].unique()), ref_structure_stride
        ):
            # Get subset of structures bassed on reference selection method
            if reference_selection == "random":
                subset_df = randomized.groupby([query_mol_id] + group_by).head(n_ref)
            else:
                # first sort by the reference selection method
                subset_df = (
                    randomized.sort_values(reference_selection)
                    .groupby([query_mol_id] + group_by)
                    .head(n_ref)
                )
            # Rank the poses by score
            scored_df = (
                subset_df.sort_values(score_column)
                .groupby([query_mol_id] + group_by)
                .head(1)
            )
            rmsd_stats_series = scored_df.groupby(group_by, group_keys=True)[
                rmsd_col
            ].apply(lambda x: x <= rmsd_cutoff).groupby(group_by).sum() / len(
                df[query_mol_id].unique()
            )

            split_cols_list = []
            score_list = []
            n_references = []

            for split_col in rmsd_stats_series.index:
                split_cols_list.append(split_col)
                score_list.append(rmsd_stats_series[split_col])
                n_references.append(n_ref)

            return_df = pd.DataFrame(
                {
                    "Fraction": score_list,
                    "Version": split_cols_list,
                    "Number of References": n_references,
                    "Structure_Split": reference_selection,
                }
            )
            if reference_selection == "random":
                return_df["Split_Value_min"] = "Random"
                return_df["Split_Value_max"] = "Random"
            else:
                return_df["Split_Value_min"] = subset_df[reference_selection].min()
                return_df["Split_Value_max"] = subset_df[reference_selection].max()
            dfs.append(return_df)

    combined = pd.concat(dfs)
    return combined

def calculate_perc_good(
    df,
    id_column: str,
    filter_column,
    filter_cutoffs: list,
    sort_column,
    n,
    split_cols: list[str],
    score_column: str,
    good_score,
    reference_col: str,
    ascending: bool = True,
    use_per_split_mol=False,
):
    """
    Calculates the percentage of 'good' scores and the percentage of molecules selected for different cutoff values
    and groups in a DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        The input DataFrame containing the data to be analyzed.
    id_column : str
        The main column used for determining membership, i.e. Compound_ID
    filter_column : str
        The name of the column used for filtering the data.
    filter_cutoffs : list
        A list of cutoff values to be used for filtering the data.
    sort_column : str
        The name of the column used for sorting the data.
    n : int
        The maximum number of rows to include in the output for each unique combination of values in `selection_cols`.
    split_cols : list
        The names of the columns used to group the data for calculating the percentage.
    score_column : str
        The name of the column containing the scores defining a good score, i.e. RMSD.
    good_score : int or float
        The threshold value used to define what is considered a 'good' score.
    use_per_split_mol : bool, optional
        Specifies whether to calculate the total number of molecules per group (`split_cols`) individually.
        If True, the percentage calculations will be based on the number of molecules per group.
        If False, the total number of molecules in the entire DataFrame will be used as the denominator.
        The default value is False.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the percentages of 'good' scores (`Percentage`), cutoff values (`cutoff_column`),
        versions (`Version`), and the percentages of molecules selected (`Percentage Docked`) for each unique
        combination of cutoff, version, and group (`split_cols`).
    """
    total_mols = len(df[id_column].unique())

    selection_cols = [id_column] + split_cols

    split_cols_list = []
    score_list = []
    cutoff_list = []
    perc_mols_list = []
    n_references = []
    for cutoff in filter_cutoffs:
        selected = get_df_subset(
            df,
            filter_column,
            cutoff,
            sort_column,
            ascending=ascending,
            selection_cols=selection_cols,
            n=n,
        )
        n_reference = selected.groupby(split_cols).nunique()[reference_col]

        if use_per_split_mol:
            total_mols = selected.groupby(split_cols)[id_column].count()

        perc_mols = selected.groupby(split_cols).nunique()[id_column] / total_mols
        score_array = calc_perc_good(
            selected, score_column, good_score, total_mols, split_cols
        )

        for split_col in score_array.index:
            split_cols_list.append(split_col)
            score_list.append(score_array[split_col])
            cutoff_list.append(cutoff)
            perc_mols_list.append(perc_mols[split_col])
            n_references.append(n_reference[split_col])

    return_df = pd.DataFrame(
        {
            f"Fraction": score_list,
            filter_column: cutoff_list,
            "Version": split_cols_list,
            "Percentage Docked": perc_mols_list,
            "Number of References": n_references,
        }
    )
    return return_df


def calculate_perc_good_wrapper(split_column_sets: dict, sort_columns, n_refs, **kwargs):
    """
    Enables the calculation of the percentage of 'good' scores for scoring functions and docking programs.

    Parameters
    ----------
    split_column_sets : dict
        A dictionary containing the names of the columns used to group the data for calculating the percentage.
        The keys are the names of the groups, and the values are lists of column names.
    sort_columns : list
        A list of the names of the columns used for sorting the data. i.e. ["POSIT_R", "RMSD", "Chemgauss4"]
    n_refs : int
        The total number of references used for docking. Used for calculating fractions.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the percentages of 'good' scores (`Fraction`), versions (`Version`), and the fraction
        of molecules selected (`Fraction of References Used`) for each unique combination of cutoff, version, and group
        (`split_cols`).
    """
    split_dfs = []
    for name, split in split_column_sets.items():
        sort_dfs = []

        for sort_column in sort_columns:
            new_df = calculate_perc_good(sort_column=sort_column,
                                       split_cols=split,
                                           **kwargs)
            new_df["Sorted_By"] = sort_column
            new_df["Fraction of References Used"] = new_df["Number of References"] / n_refs
            sort_dfs.append(new_df)
        split_combined = pd.concat(sort_dfs)
        split_combined["Split"] = name
        split_dfs.append(split_combined)
    combined = pd.concat(split_dfs)
    return combined


# I don't think this function should be necessary after changing how I'm doing the structure splits
def calculate_stats(df,
                    metric_dict,
                    summary_col,
                    filter_column,
                    filter_cutoffs,
                    value_column,
                    extra_groupby_cols=None):
    """
    Calculates the mean and standard deviation of a metric for different cutoff values and groups in a DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        The input DataFrame containing the data to be analyzed.
    metric_dict : dict
        A dictionary containing the names of the metrics to be calculated. The keys are the names of the metrics, and
        the values are the functions used to calculate the metrics.
    summary_col : str
        The name of the column used to group the data for calculating the metrics.
    filter_column : str
        The name of the column used to filter the data.
    filter_cutoffs : list
        A list of the cutoff values used to filter the data.
    value_column : str
        The name of the column containing the values to be analyzed.
    extra_groupby_cols : list, optional
        A list of the names of the columns used to group the data for calculating the metrics. The default value is None.
    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the mean and standard deviation of the metrics (`Value`), the names of the metrics
    """
    groupby_cols = [summary_col] + extra_groupby_cols
    dfs = []
    for name, metric in metric_dict.items():
        means = []
        cutoffs = []
        summary_types = []
        sds = []
        for cutoff in filter_cutoffs:
            values = df[df[filter_column] <= cutoff].groupby(groupby_cols, group_keys=True)[value_column].apply(metric)
            mean_list = values.groupby([summary_col]).mean()
            sd_list = values.groupby([summary_col]).std()
            for summary_type in mean_list.index:
                means.append(mean_list[summary_type])
                cutoffs.append(cutoff)
                summary_types.append(summary_type)
                sds.append(sd_list[summary_type])
        mean_df = pd.DataFrame(
            {f"Value": means, "Metric": name, filter_column: cutoffs, summary_col: summary_types, "STD": sds})
        dfs.append(mean_df)

    return pd.concat(dfs)