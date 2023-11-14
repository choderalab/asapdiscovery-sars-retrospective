import pandas as pd
from typing import Union
from pydantic import BaseModel, Field, PrivateAttr
from enum import Enum
from typing import Any


class StructureSplitType(Enum):
    RANDOM = "random"
    ASCENDING = "ascending"
    DESCENDING = "descending"


class ScoreType(Enum):
    RMSD = "RMSD"


class AnalysisWorkflow(BaseModel):

    df: pd.DataFrame
    query_mol_id: str # Column name of the molecule ID
    group_by: list[str] # Column names to group by
    ref_structure_id: str = Field("Structure_Name",description="Column name of the reference structure ID")
    structure_split: StructureSplitType = Field(StructureSplitType.RANDOM, description="How to split the structures")
    fraction_structures_used: float = 1.0,
    rmsd_col: str = "RMSD",
    rmsd_cutoff: float = 2.0,
    count_nrefs: bool = False

    processed: pd.DataFrame = Field(default=None, description="Dataframe after processing")
    structure_sorted: Any = Field(default=None, description="Dataframe GroupBy object after sorting by structure")
    scored: Any = Field(default=None, description="Dataframe GroupBy object after sorting by score")
    fraction_success: Any = Field(default=None, description="Fraction of molecules that are within the RMSD cutoff")
    number_of_molecules: int = Field(default=None, description="Number of molecules in the dataset")
    number_of_structures: int = Field(default=None, description="Number of structures in the dataset")
    combined_df: pd.DataFrame = Field(default=None, description="Combined results dataframe")
    return_df: pd.DataFrame = Field(default=None, description="Combined restuls dataframe with statistics")

    _return_dfs: list[pd.DataFrame] = PrivateAttr(default=[])
    _n_struc: int = PrivateAttr(default=None)
    _randomized: pd.DataFrame = PrivateAttr(default=None)

    def run_workflow(self, score_column: str, structure_split: StructureSplitType, rmsd_col: str = "RMSD", rmsd_cutoff: Union[int, float] = 2, n_bootstraps: int = 3, ref_structure_stride: int = 10, cumulative: bool=True, top_n_scores: int = 1):
        self.initialize()
        self._return_dfs = []
        for i in range(n_bootstraps):
            self.randomize()
            self.sort_by_structure_split(structure_split)
            for n_struc in range(1, self.number_of_structures, ref_structure_stride):
                self.get_n_structures(n_struc)
                self.sort_by_score(score_column)
                self.get_n_scores(top_n_scores)
                self.calculate_fraction_success(rmsd_col, rmsd_cutoff)
                self.collect_results()

        self.combined_df = pd.concat(self._return_dfs)

        self.calculate_errors()
        return self.return_df

    def initialize(self):
        self.number_of_structures = self.df[self.ref_structure_id].nunique()
        self.number_of_molecules = self.df[self.query_mol_id].nunique()

    def randomize(self):
        # Randomize the order of the structures, necessary for bootstrapping to be useful
        self._randomized = self.df.sample(frac=1)

    def sort_by_structure_split(self, structure_split=None):
        if structure_split:
            self.structure_split = structure_split
        else:
            structure_split = self.structure_split
        if not structure_split:
            raise ValueError("structure_split must be specified")
        self.structure_sorted = self._randomized.sort_values(structure_split).groupby([self.query_mol_id] + self.group_by)

    def get_n_structures(self, n_struc: int):
        self._n_struc = n_struc
        self.processed = self.structure_sorted.head(self._n_struc)
        # self.processed = self._randomized.sort_values(self.structure_split).groupby([self.query_mol_id] + self.group_by).head(self._n_struc)

    def sort_by_score(self, score_column):
        # Rank the poses by score
        self.scored = self.processed.sort_values(score_column).groupby([self.query_mol_id] + self.group_by)

    def get_n_scores(self, n_scores: int):
        self.processed = self.scored.head(n_scores)

    def calculate_fraction_success(self, rmsd_col, rmsd_cutoff):
        self.fraction_success = self.processed.groupby(self.group_by, group_keys=True)[rmsd_col].apply(lambda x: x <= rmsd_cutoff).groupby(self.group_by).sum() / self.number_of_molecules

    def collect_results(self):
        split_cols_list = []
        score_list = []
        n_references = []

        for split_col in self.fraction_success.index:
            split_cols_list.append(split_col)
            score_list.append(self.fraction_success[split_col])
            n_references.append(self._n_struc)

        # n_allowed_refs = n_references if cumulative else ref_structure_stride

        return_df = pd.DataFrame(
            {
                "Fraction": score_list,
                "Version": split_cols_list,
                "Number of References": n_references,
                "Structure_Split": self.structure_split,
            }
        )

        # TODO: move to before scoring
        if self.structure_split == "random":
            return_df["Split_Value_min"] = "Random"
            return_df["Split_Value_max"] = "Random"
        else:
            return_df["Split_Value_min"] = self.processed[self.structure_split].min()
            return_df["Split_Value_max"] = self.processed[self.structure_split].max()

        self._return_dfs.append(return_df)

    def calculate_errors(self):
        grouped_df = self.combined_df.groupby(["Version", "Number of References", "Structure_Split", "Split_Value_min", "Split_Value_max"])
        self.return_df = grouped_df.mean().reset_index()
        self.return_df["Fraction_Upper_Error"] = grouped_df.quantile(0.975).reset_index()["Fraction"]
        self.return_df["Fraction_Lower_Error"] = grouped_df.quantile(0.025).reset_index()["Fraction"]

    class Config:
        arbitrary_types_allowed = True


