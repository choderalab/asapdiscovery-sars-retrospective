from pydantic import BaseModel, Field, model_validator, field_validator
import pandas as pd
from pyarrow import parquet as pq
import pyarrow as pa
from abc import abstractmethod


class ColumnName:

    def __init__(self, value: str, is_key: bool = False):
        self.value = value
        self.is_key = is_key

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class KeyColumn(ColumnName):
    def __init__(self, value: str):
        super().__init__(value, is_key=True)


class ValueColumn(ColumnName):
    def __init__(self, value: str):
        super().__init__(value, is_key=False)


REFERENCE_COLUMN = KeyColumn("Reference_Structure")
QUERY_COLUMN = KeyColumn("Query_Ligand")
POSE_ID_COLUMN = KeyColumn("Pose_ID")


class DataFrameModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    dataframe: pd.DataFrame = Field(
        ...,
        description="DataFrame containing model data",
    )

    def __eq__(self, other):
        if not isinstance(other, DataFrameModel):
            return False
        return (
            self.dataframe.equals(other.dataframe)
            and self.get_parquet_metadata() == other.get_parquet_metadata()
        )

    @field_validator("*", mode="before")
    @classmethod
    def convert_column_names(cls, v):
        """Convert string fields to appropriate ColumnName types"""
        if isinstance(v, str):
            # Get the field info from the model
            field_info = next(
                (
                    field
                    for field in cls.model_fields.values()
                    if field.default
                    and isinstance(field.default, ColumnName)
                    and str(field.default) == v
                ),
                None,
            )
            if field_info:
                # Convert to the same type as the default
                return field_info.default.__class__(v)
        return v

    def get_columns(self) -> list[str]:
        """Get the columns from the DataFrame."""
        columns = []
        for field_name, field_value in self:
            if isinstance(field_value, ColumnName):
                columns.append(field_value.value)
        return columns

    @model_validator(mode="after")
    def check_columns_in_dataframe(self):
        columns = self.get_columns()
        for column in columns:
            if column not in self.dataframe.columns:
                raise ValueError(
                    f"Column '{column}' specified in metadata is not present in the DataFrame."
                )

    def get_parquet_metadata(self) -> dict:
        return {str(k): str(v) for k, v in self.dict().items() if k != "dataframe"}

    @staticmethod
    def parse_parquet_metadata(metadata: dict) -> dict:
        return {k.decode("utf-8"): v.decode("utf-8") for k, v in metadata.items()}

    def to_parquet(self, path: str):
        table = pa.Table.from_pandas(self.dataframe)
        table = table.replace_schema_metadata(self.get_parquet_metadata())
        pq.write_table(table, path)

    def to_csv(self, path: str):
        self.dataframe.to_csv(path, index=False)

    @classmethod
    def from_csv(cls, path: str, **kwargs) -> "DataFrameModel":
        return cls(dataframe=pd.read_csv(path), **kwargs)

    @classmethod
    def from_parquet(cls, path: str) -> "DataFrameModel":
        table = pq.read_table(path)
        metadata = cls.parse_parquet_metadata(table.schema.metadata)
        return cls(dataframe=table.to_pandas(), **metadata)


class PairwiseData(DataFrameModel):
    reference_column: KeyColumn = Field(
        REFERENCE_COLUMN, description="Reference structure column"
    )
    query_column: KeyColumn = Field(QUERY_COLUMN, description="Query structure column")


class PoseData(PairwiseData):
    pose_id_column: KeyColumn = Field(POSE_ID_COLUMN, description="Pose ID column")
    rmsd_column: ValueColumn = Field(ValueColumn("RMSD"), description="RMSD column")

    def get_key_columns(self) -> list[str]:
        return [
            self.reference_column.value,
            self.query_column.value,
            self.pose_id_column.value,
        ]

    def get_value_columns(self) -> list[str]:
        return [self.rmsd_column.value]


class ChemicalSimilarityData(PairwiseData):
    tanimoto_column: ValueColumn = Field(
        ValueColumn("Tanimoto"), description="Tanimoto similarity column"
    )
    other_columns: list[ColumnName] = Field(
        [],
        description="Other columns",
    )

    def get_columns(self) -> list[str]:
        columns = super().get_columns()
        columns.extend([str(col) for col in self.other_columns])
        return columns

    def get_parquet_metadata(self) -> dict:
        metadata = {
            str(k): str(v)
            for k, v in super().get_parquet_metadata().items()
            if k not in ["other_columns"]
        }
        metadata.update(
            {
                str(v): "key_column" if v.is_key else "value_column"
                for v in self.other_columns
            }
        )
        return metadata

    @staticmethod
    def parse_parquet_metadata(metadata: dict) -> dict:
        parsed_metadata = DataFrameModel.parse_parquet_metadata(metadata)
        parsed_metadata["other_columns"] = [
            ColumnName(k, v == "key_column")
            for k, v in parsed_metadata.items()
            if v in ["key_column", "value_column"]
        ]
        return parsed_metadata


#
#
# class DockingDataModel(BaseModel):
#
#     pose_data: PoseData = Field(..., description="Pose data")
#     chemical_similarity_data: ChemicalSimilarityData = Field(
#         ..., description="Chemical similarity data"
#     )
