from pydantic import BaseModel, Field, model_validator, field_validator
import pandas as pd
from pyarrow import parquet as pq
import pyarrow as pa
from pathlib import Path
from enum import StrEnum


class ColumnType(StrEnum):
    """Enum for column types."""

    KEY = "key"
    VALUE = "value"
    PARAM = "param"


class ColumnName(BaseModel):
    name: str = Field(..., description="Column name")
    column_type: ColumnType

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


REFERENCE_COLUMN = KeyColumn(name="Reference_Structure")
QUERY_COLUMN = KeyColumn(name="Query_Ligand")
POSE_ID_COLUMN = KeyColumn(name="Pose_ID")


class DataFrameModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True

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

    def get_columns(self, column_type=None | ColumnType) -> list[ColumnName]:
        """Get all column names from model fields."""
        columns = []
        for field_value in self.__dict__.values():
            if isinstance(field_value, ColumnName):
                columns.append(field_value)
            elif isinstance(field_value, list):
                columns.extend(
                    col for col in field_value if isinstance(col, ColumnName)
                )
        if column_type:
            columns = [col for col in columns if col.column_type == column_type]
        return columns

    def to_parquet_metadata(self) -> dict:
        """Convert model fields to parquet metadata."""
        metadata = {}
        for field_name, field_value in self:
            if field_name == "dataframe":
                continue
            if isinstance(field_value, ColumnName):
                metadata[field_name] = field_value.name
            elif isinstance(field_value, list):
                for col in field_value:
                    if isinstance(col, ColumnName):
                        metadata[col.name] = col.column_type.value
        return metadata

    @model_validator(mode="after")
    def check_columns_in_dataframe(self):
        columns = self.get_columns()
        for column in columns:
            if column.name not in self.dataframe.columns:
                raise ValueError(
                    f"Column '{column}' specified in metadata is not present in the DataFrame."
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
            if field.annotation in [KeyColumn, ValueColumn, ParamColumn]:
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
    reference_column: KeyColumn = Field(
        REFERENCE_COLUMN, description="Reference structure column"
    )


class QueryData(DataFrameModel):
    query_column: KeyColumn = Field(QUERY_COLUMN, description="Query structure column")


class PairwiseData(ReferenceData, QueryData):
    pass


class PoseData(PairwiseData):
    pose_id_column: KeyColumn = Field(POSE_ID_COLUMN, description="Pose ID column")
    rmsd_column: ValueColumn = Field(
        ValueColumn(name="RMSD"), description="RMSD column"
    )


class ChemicalSimilarityData(PairwiseData):
    type: ParamColumn = Field(..., description="Type of similarity")
    tanimoto_column: ValueColumn = Field(
        ValueColumn(name="Tanimoto"), description="Tanimoto similarity column"
    )


class DockingDataModel(BaseModel):

    pose_data: PoseData = Field(..., description="Pose data")
    chemical_similarity_data: list[ChemicalSimilarityData] = Field(
        [], description="Chemical similarity data"
    )

    def to_parquet(self, path: str | Path):
        path = Path(path)
        self.pose_data.to_parquet(path / f"pose_data.parquet")

        for similarity in self.chemical_similarity_data:
            similarity.to_parquet(path.replace(".parquet", f"_{similarity}.parquet"))
