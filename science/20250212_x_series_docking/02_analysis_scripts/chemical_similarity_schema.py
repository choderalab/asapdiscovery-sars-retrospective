from pydantic import BaseModel, Field, confloat, root_validator, ValidationError
from enum import Enum
import json
import pandas as pd


class MoleculeSimilarity(BaseModel):
    """
    MoleculeSimilarity
    """

    mol1: str = Field(..., description="Molecule 1")
    mol2: str = Field(..., description="Molecule 2")
    type: str = Field(..., description="Type of similarity")
    tanimoto: confloat(ge=0, le=1) = Field(
        ..., description="Tanimoto similarity from 0 to 1"
    )

    def save(self, path):
        with open(path, "w") as f:
            json.dump(self.dict(), f, indent=4)

    @classmethod
    def load(cls, path):
        with open(path, "r") as f:
            return cls(**json.load(f))

    def __str__(self):
        return f"{self.type} similarity between {self.mol1} and {self.mol2}: {self.tanimoto}"

    @classmethod
    def construct_dataframe(cls, similarity_list):
        return pd.DataFrame.from_records(
            [similarity.dict() for similarity in similarity_list]
        )


class ECFPSimilarity(MoleculeSimilarity):
    """
    ECFPSimilarity
    """

    type: str = Field("ECFP", description="Type of similarity")
    radius: int = 2
    bitsize: int = 2048

    @property
    def fingerprint(self):
        return f"ECFP{self.radius * 2}_{self.bitsize}"

    # add fingerprint property to output dictionary
    def dict(self, *args, **kwargs):
        return_dict = super().dict()
        return_dict.update({"fingerprint": self.fingerprint})
        return return_dict


class MCSSimilarity(MoleculeSimilarity):
    """
    MCSSimilarity
    """

    type: str = Field("MCS", description="Type of similarity")
    num_atoms_in_mcs: int = Field(..., description="Number of atoms in the MCS")
    num_atoms_in_union: int = Field(
        ..., description="Total number of atoms between the two molecules"
    )

    @root_validator(pre=True)
    @classmethod
    def validate_tanimoto(cls, values):
        if "num_atoms_in_mcs" in values and "num_atoms_in_union" in values:
            expected_tanimoto = (
                values["num_atoms_in_mcs"] / values["num_atoms_in_union"]
            )
            assert (
                abs(values["tanimoto"] - expected_tanimoto) < 0.0001
            ), f"Tanimoto {values['tanimoto']} does not match expected value {expected_tanimoto}"
        return values


class TanimotoComboType(str, Enum):
    """
    Enum for the different types of Tanimoto coefficients that can be calculated.
    """

    SHAPE = "TanimotoShape"
    COLOR = "TanimotoColor"
    COMBO = "TanimotoCombo"


class TanimotoComboSimilarity(MoleculeSimilarity):
    """
    TanimotoComboSimilarity
    """

    type: str = Field("TanimotoCombo", description="Type of similarity")
    tanimoto_shape: confloat(ge=0, le=1) = Field(..., description="Shape Tanimoto")
    tanimoto_color: confloat(ge=0, le=1) = Field(..., description="Color Tanimoto")

    @classmethod
    def from_tanimoto_results(cls, mol1, mol2, results):
        """
        This uses the OpenEye results class to get the TanimotoCombo similarity.
        :param mol1:
        :param mol2:
        :param results:
        :return:
        """
        return cls(
            mol1=mol1,
            mol2=mol2,
            tanimoto=results.GetTanimotoCombo(),
            tanimoto_shape=results.GetShapeTanimoto(),
            tanimoto_color=results.GetColorTanimoto(),
        )


# just test within this file
if __name__ == "__main__":
    ecfp = ECFPSimilarity(
        mol1="mol1",
        mol2="mol2",
        tanimoto=0.5,
    )
    ecfp.save("ecfp.json")
    ecfp2 = ECFPSimilarity.load("ecfp.json")
    assert ecfp == ecfp2

    mcs = MCSSimilarity(
        mol1="mol1",
        mol2="mol2",
        num_atoms_in_mcs=5,
        num_atoms_in_union=10,
        tanimoto=0.5,
    )
    mcs.save("mcs.json")
    mcs2 = MCSSimilarity.load("mcs.json")

    try:
        mcs3 = MCSSimilarity(
            mol1="mol1",
            mol2="mol2",
            num_atoms_in_mcs=5,
            num_atoms_in_union=10,
            tanimoto=0.6,
        )
        raise AssertionError("Tanimoto should not match")
    except ValidationError as e:
        print("Success")

    # test dataframe construction
    df = MoleculeSimilarity.construct_dataframe([ecfp, ecfp2, mcs, mcs2])
    df.to_csv("similarity.csv", index=False)
