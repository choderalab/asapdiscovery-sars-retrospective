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