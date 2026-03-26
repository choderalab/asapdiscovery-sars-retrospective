from pydantic import BaseModel, Field, model_validator, field_validator, ConfigDict
import pandas as pd
from pyarrow import parquet as pq
import pyarrow as pa
from pathlib import Path
from enum import Enum, StrEnum
from operator import eq, gt, lt, ge, le, ne


class ColumnType(StrEnum):
    """Enum for column types."""

    KEY = "key"
    VALUE = "value"
    PARAM = "param"
    INFO = "info"

    def __or__(self, other):
        if not isinstance(other, ColumnType):
            return NotImplemented
        return (self, other)


class ColumnName(BaseModel):
    name: str = Field(..., description="Column name")
    column_type: ColumnType
    required: bool = Field(True, description="Is this column required?")

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"{self.column_type.value}:{self.name}"


class ValueColumn(ColumnName):
    """Class for value columns."""

    column_type: ColumnType = Field(ColumnType.VALUE, description="Column type")


class KeyColumn(ColumnName):
    """Class for key columns."""

    column_type: ColumnType = Field(ColumnType.KEY, description="Column type")


class ParamColumn(ColumnName):
    """Class for parameter columns."""

    column_type: ColumnType = Field(ColumnType.PARAM, description="Column type")


class InfoColumn(ColumnName):
    """Class for info columns."""

    column_type: ColumnType = Field(ColumnType.INFO, description="Column type")


ColumnNames = InfoColumn | KeyColumn | ValueColumn | ParamColumn


REFERENCE_COLUMN = KeyColumn(name="Reference_Structure")
QUERY_COLUMN = KeyColumn(name="Query_Ligand")
POSE_ID_COLUMN = KeyColumn(name="Pose_ID")


class DataFrameType(StrEnum):
    """Enum for DataFrame types."""

    REFERENCE = "ReferenceData"
    QUERY = "QueryData"
    POSE = "PoseData"
    CHEMICAL_SIMILARITY = "ChemicalSimilarityData"

    def __or__(self, other):
        if not isinstance(other, DataFrameType):
            return NotImplemented
        return (self, other)

class DataFrameModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: InfoColumn = Field(..., description="Name of the dataframe model")

    dataframe: pd.DataFrame = Field(
        ...,
        description="DataFrame containing model data",
    )
    other_columns: list[ColumnName] = Field(
        [],
        description="Other columns",
    )

    def __eq__(self, other):
        if not isinstance(other, DataFrameModel):
            return False
        return (
            self.dataframe.equals(other.dataframe)
            and self.to_parquet_metadata() == other.to_parquet_metadata()
        )

    def get_columns(
            self, column_type: ColumnType | None = None, as_str: bool = False
    ) -> list[ColumnNames | str]:
        """Get all column names from model fields."""
        columns = self.columns

        # Filter by column type if specified
        if column_type:
            columns = [col for col in columns if col.column_type in column_type]

        return [str(col) for col in columns] if as_str else columns

    def to_parquet_metadata(self) -> dict:
        """Convert model fields to parquet metadata."""
        metadata = {}
        for field_name, field_value in self:
            if field_name == "dataframe":
                continue
            elif isinstance(field_value, ColumnName):
                metadata[field_name] = field_value.name
            elif isinstance(field_value, list):
                for col in field_value:
                    if isinstance(col, ColumnName):
                        metadata[col.name] = col.column_type.value
            else:
                print(field_name, field_value)
                metadata[field_name] = field_value
        return metadata

    @model_validator(mode="after")
    def check_columns_in_dataframe(self):
        non_info_types = tuple(col_type for col_type in ColumnType if col_type != ColumnType.INFO)
        in_df_columns = self.get_columns(non_info_types, as_str=True)
        for column in in_df_columns:
            if column not in self.dataframe.columns:
                raise ValueError(
                    f"Column '{column}' specified in metadata is not present in the DataFrame."
                )
        df_columns = set(self.dataframe.columns)
        for column in df_columns:
            if column not in self.get_columns(as_str=True):
                raise ValueError(
                    f"Column '{column}' in DataFrame is not specified in metadata."
                )

    @classmethod
    def from_parquet_metadata(cls, metadata: dict) -> dict:
        """Convert parquet metadata back to model fields."""
        parsed_metadata = {
            k.decode("utf-8"): v.decode("utf-8") for k, v in metadata.items()
        }

        result = {}
        # Handle model fields with ColumnName types
        for field_name, field in cls.model_fields.items():
            if field_name == "dataframe":
                continue
            elif field.annotation in [KeyColumn, ValueColumn, ParamColumn, InfoColumn]:
                if field_name in parsed_metadata:
                    result[field_name] = field.annotation(
                        name=parsed_metadata[field_name]
                    )

        # Handle other columns that were stored as column_name: column_type pairs
        other_columns = []
        for name, type_value in parsed_metadata.items():
            if type_value in ColumnType.__members__.values():
                column_type = ColumnType(type_value)
                other_columns.append(ColumnName(name=name, column_type=column_type))
            else:
                # if we haven't already parsed it
                if name not in result:
                    result[name] = parsed_metadata[name]

        if other_columns:
            result["other_columns"] = other_columns
        return result

    def to_parquet(self, path: str | Path):
        table = pa.Table.from_pandas(self.dataframe)
        table = table.replace_schema_metadata(self.to_parquet_metadata())
        pq.write_table(table, path)

    def to_csv(self, path: str):
        self.dataframe.to_csv(path, index=False)

    @classmethod
    def from_csv(cls, path: str, **kwargs) -> "DataFrameModel":
        return cls(dataframe=pd.read_csv(path), **kwargs)

    @classmethod
    def from_parquet(cls, path: str) -> "DataFrameModel":
        table = pq.read_table(path)
        metadata = cls.from_parquet_metadata(table.schema.metadata)
        return cls(dataframe=table.to_pandas(), **metadata)


class ReferenceData(DataFrameModel):
    type: DataFrameType = Field(DataFrameType.REFERENCE, description="Type of data")
    name: InfoColumn = Field(InfoColumn(name="ReferenceData"), description="Type of data")
    reference_column: KeyColumn = Field(
        REFERENCE_COLUMN, description="Reference structure column"
    )

    @property
    def columns(self):
        return [self.name, self.reference_column] + self.other_columns


class QueryData(DataFrameModel):
    type: DataFrameType = Field(DataFrameType.QUERY, description="Type of data")
    name: InfoColumn = Field(InfoColumn(name="QueryData"), description="Type of data")
    query_column: KeyColumn = Field(QUERY_COLUMN, description="Query structure column")

    @property
    def columns(self):
        return [self.name, self.query_column] + self.other_columns


class PairwiseData(ReferenceData, QueryData):
    name: InfoColumn = Field(InfoColumn(name="PairwiseData"), description="Type of data")
    pass

    @property
    def columns(self):
        return [self.name, self.reference_column, self.query_column] + self.other_columns


class PoseData(PairwiseData):
    type: DataFrameType = Field(DataFrameType.POSE, description="Type of data")
    name: InfoColumn = Field(InfoColumn(name="PoseData"), description="Type of data")
    pose_id_column: KeyColumn = Field(POSE_ID_COLUMN, description="Pose ID column")
    rmsd_column: ValueColumn = Field(
        ValueColumn(name="RMSD"), description="RMSD column"
    )
    @property
    def columns(self):
        return [self.name, self.reference_column, self.query_column, self.pose_id_column, self.rmsd_column] + self.other_columns


class ChemicalSimilarityData(PairwiseData):
    type: DataFrameType = Field(DataFrameType.CHEMICAL_SIMILARITY, description="Type of data")
    name: InfoColumn = Field(..., description="Type of data")
    tanimoto_column: ValueColumn = Field(
        ValueColumn(name="Tanimoto"), description="Tanimoto similarity column"
    )

    @property
    def columns(self):
        return [self.name, self.reference_column, self.query_column, self.tanimoto_column] + self.other_columns



def get_common_columns(
    dataframes: list[DataFrameModel], column_type: ColumnType = None
) -> list[str]:
    """Get common columns across multiple DataFrames."""
    common_columns = set(dataframes[0].get_columns(column_type, as_str=True))
    for df in dataframes[1:]:
        common_columns.intersection_update(
            set(df.get_columns(column_type, as_str=True))
        )
    return list(common_columns)



class Operator(StrEnum):
    EQ = "eq"
    GT = "gt"
    LT = "lt"
    GE = "ge"
    LE = "le"
    NE = "ne"
    IN = "in"

    def to_callable(self) -> callable:
        def isin(x, value):
            if isinstance(value, (list, tuple, set)):
                return x in value
            return False

        return {
            self.EQ: eq,
            self.GT: gt,
            self.LT: lt,
            self.GE: ge,
            self.LE: le,
            self.NE: ne,
            self.IN: isin
        }[self]

class ColumnFilter(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    data_type: DataFrameType = Field(..., description="Type of data")
    column: ColumnName = Field(..., description="Column to filter on")
    value: str | int | float | list
    operator: Operator = Operator.EQ

    @model_validator(mode="after")
    def match_operator_with_value(self):
        if self.operator == Operator.IN and not isinstance(self.value, (list, tuple)):
            raise ValueError("Operator 'in' requires value to be a list or tuple.")
        if self.operator != Operator.IN and isinstance(self.value, (list, tuple)):
            raise ValueError("Operator 'in' is only valid for list or tuple values.")
        return self

    def filter(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        if self.column.name not in dataframe.columns:
            raise ValueError(f"Column '{self.column.name}' not found in DataFrame.")
        return dataframe[
            dataframe[self.column.name].apply(lambda x: self.operator.to_callable()(x, self.value))
        ]
class ColumnTake(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    take_column: ColumnName = Field(..., description="Columns to take")
    sort_columns: list[ColumnName] = Field([], description="Columns to sort by")
    ascending: bool = Field(True, description="Sort order")
    n: int = Field(1, description="Number of rows to take")
    def take(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        if self.take_column.name not in dataframe.columns:
            raise ValueError(f"Column '{self.take_column.name}' not found in DataFrame.")
        if self.sort_columns:
            sort_columns = [col.name for col in self.sort_columns]
            dataframe = dataframe.sort_values(by=sort_columns, ascending=self.ascending)
        return dataframe.head(self.n)[self.take_column.name]

class DockingDataModel:
    def __init__(
        self,
        reference_data: ReferenceData,
        query_data: QueryData,
        pose_data: PoseData,
        chemical_similarity_data: list[ChemicalSimilarityData] | None = None,
    ):
        self.reference_data = reference_data
        self.query_data = query_data
        self.pose_data = pose_data
        self.chemical_similarity_data = chemical_similarity_data or []

    def __repr__(self):
        return f"DockingDataModel(reference_data={self.reference_data}, query_data={self.query_data}, pose_data={self.pose_data}, chemical_similarity_data={self.chemical_similarity_data})"

    def get_dataframe_list(self):
        return [self.reference_data, self.query_data, self.pose_data] + self.chemical_similarity_data

    def get_data_as_dict(self) -> dict[str, DataFrameModel]:
        dataframes = {}
        for data in self.get_dataframe_list():
            dataframes[str(data.name)] = data
        return dataframes

    def get_key_columns(self):
        key_columns = []
        for data in self.get_dataframe_list():
            key_columns.extend(
                [col for col in data.get_columns(ColumnType.KEY, as_str=True)]
            )
        return set(key_columns)

    def get_value_columns(self):
        key_columns = []
        for data in self.get_dataframe_list():
            key_columns.extend(
                [col for col in data.get_columns(ColumnType.VALUE, as_str=True)]
            )
        return set(key_columns)

    def get_combined_similarity_data(self) -> pd.DataFrame:
        if self.chemical_similarity_data is None:
            return pd.DataFrame()
        combined_similarity_data = self.chemical_similarity_data[0].dataframe.copy()

        if len(self.chemical_similarity_data) == 1:
            return combined_similarity_data

        # Get common columns for merging
        similarity_columns = get_common_columns(self.chemical_similarity_data)
        for similarity_data in self.chemical_similarity_data[1:]:
            combined_similarity_data = pd.merge(
                combined_similarity_data,
                similarity_data.dataframe,
                on=similarity_columns,
                how="outer",
            )
        return combined_similarity_data

    def get_combined_dataframe(self):
        # Ensure we have the required base data
        if self.pose_data.dataframe.empty:
            raise ValueError("Pose data is empty")

        # Start with pose data
        combined_df = self.pose_data.dataframe.copy()

        # Merge reference and query data
        for data_model in [self.reference_data, self.query_data]:
            if data_model.dataframe.empty:
                raise ValueError(f"{data_model.__class__.__name__} is empty")

            combined_df = pd.merge(
                combined_df,
                data_model.dataframe,
                on=data_model.get_columns(column_type=(ColumnType.KEY), as_str=True),
                how="inner",
            )

        # Merge similarity data if exists
        if self.chemical_similarity_data:
            try:
                similarity_df = self.get_combined_similarity_data()
                if not similarity_df.empty:
                    key_cols = self.chemical_similarity_data[0].get_columns('key', as_str=True)
                    combined_df = pd.merge(
                        combined_df,
                        similarity_df,
                        on=key_cols,
                        how="inner",
                    )
            except (IndexError, KeyError) as e:
                print(f"Warning: Could not merge similarity data: {e}")

        return combined_df

    def copy(self) -> "DockingDataModel":
        # Create new instances of each data model with copied dataframes
        new_reference = ReferenceData(
            dataframe=self.reference_data.dataframe.copy(),
            name=self.reference_data.name,
            reference_column=self.reference_data.reference_column,
            other_columns=self.reference_data.other_columns
        )
        new_query = QueryData(
            dataframe=self.query_data.dataframe.copy(),
            name=self.query_data.name,
            query_column=self.query_data.query_column,
            other_columns=self.query_data.other_columns
        )
        new_pose = PoseData(
            dataframe=self.pose_data.dataframe.copy(),
            name=self.pose_data.name,
            reference_column=self.pose_data.reference_column,
            query_column=self.pose_data.query_column,
            pose_id_column=self.pose_data.pose_id_column,
            rmsd_column=self.pose_data.rmsd_column,
            other_columns=self.pose_data.other_columns
        )
        new_similarity = [
            ChemicalSimilarityData(
                dataframe=data.dataframe.copy(),
                name=data.name,
                reference_column=data.reference_column,
                query_column=data.query_column,
                tanimoto_column=data.tanimoto_column,
                other_columns=data.other_columns
            )
            for data in self.chemical_similarity_data
        ] if self.chemical_similarity_data else None

        # Create new DockingDataModel
        return DockingDataModel(
            reference_data=new_reference,
            query_data=new_query,
            pose_data=new_pose,
            chemical_similarity_data=new_similarity
        )


    def apply_filters(self, filters: list[ColumnFilter]) -> "DockingDataModel":
        """
        Create a new DockingDataModel with filtered DataFrameModels.

        Args:
            filters: List of ColumnFilter objects to apply

        Returns:
            New DockingDataModel instance with filtered data
        """
        # Create new instances of each data model with copied dataframes
        new_data = self.copy()

        # Apply filters
        for data in new_data.get_dataframe_list():
            for cf in filters:
                if cf.column in data.get_columns():
                    data.dataframe = cf.filter(data.dataframe)

        return new_data

    def get_unique_refs(self):
        """
        Get unique reference structures from the reference data.
        """
        ref_data = self.reference_data
        return ref_data.dataframe[ref_data.reference_column.name].unique()

    def get_unique_ligs(self):
        """
        Get unique query ligands from the query data.
        """
        query_data = self.query_data
        return query_data.dataframe[query_data.query_column.name].unique()
