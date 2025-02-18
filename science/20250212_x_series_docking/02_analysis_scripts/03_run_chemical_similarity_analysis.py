"""
Script to generate chemical similarity analysis between reference and query ligands in a docking experiment.
"""

from rdkit import Chem
from rdkit.Chem.rdFMCS import FindMCS
from asapdiscovery.data.backend.openeye import oechem, oeshape
from openeye import oegraphsim  # not in asap repo
from asapdiscovery.data.readers.molfile import MolFileFactory
from asapdiscovery.data.schema.ligand import Ligand
import pandas as pd
import itertools
import argparse
from pebble import ProcessPool
from concurrent.futures import TimeoutError
import multiprocessing as mp
from tqdm import tqdm
from pathlib import Path
from pydantic import BaseSettings
import json
from functools import partial


def parse_args():
    parser = argparse.ArgumentParser(
        description="Combine results csvs and generate input csv for full cross docking evaluation"
    )
    parser.add_argument(
        "--ref-ligand-sdf",
        type=Path,
        required=True,
        help="Path to directory containing prepped reference ligand sdf.",
    )
    parser.add_argument(
        "--output-dir", required=True, type=Path, help="Path to output directory"
    )
    parser.add_argument(
        "--query-ligand-sdf",
        type=Path,
        required=False,
        help="Path to directory containing prepped query ligand sdf.  If false, ref-ligand-sdf will be used.",
    )
    parser.add_argument(
        "--settings", type=Path, required=False, help="Path to settings json file"
    )
    parser.add_argument(
        "--n-processes",
        type=int,
        default=None,
        help="Number of processes to use (default: number of CPU cores)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout in seconds for each pair calculation (default: 300)",
    )
    return parser.parse_args()


def get_fp(mol, bit_size=2048, radius=2):
    fp = oegraphsim.OEFingerPrint()
    oegraphsim.OEMakeCircularFP(
        fp,
        mol,
        bit_size,
        0,
        radius,
        oegraphsim.OEFPAtomType_DefaultCircularAtom,
        oegraphsim.OEFPBondType_DefaultCircularBond,
    )
    return fp


def calculate_tanimoto(fp1, fp2):
    return oegraphsim.OETanimoto(fp1, fp2)


def calculate_tanimoto_combo(refmol: oechem.OEMol, querymol: oechem.OEMol):
    # Prepare reference molecule for calculation
    # With default options this will remove any explicit hydrogens present
    prep = oeshape.OEOverlapPrep()
    prep.Prep(refmol)

    # Get appropriate function to calculate exact shape
    shapeFunc = oeshape.OEOverlapFunc()
    shapeFunc.SetupRef(refmol)

    res = oeshape.OEOverlapResults()
    prep.Prep(querymol)
    shapeFunc.Overlap(querymol, res)
    return res.GetTanimotoCombo()


class Settings(BaseSettings):
    ECFP_Tanimoto: bool = True
    ECFP_Radius: int = 2
    ECFP_BitSize: int = 2048
    OETanimotoCombo: bool = False
    MCS_Tanimoto: bool = True

    @property
    def Fingerprint(self):
        return f"ECFP{self.ECFP_Radius*2}_{self.ECFP_BitSize}"

    def save(self, path):
        with open(path, "w") as f:
            f.write(self.json(indent=4))

    @classmethod
    def load(cls, path):
        with open(path, "r") as f:
            return cls(**json.load(f))


def get_relevant_mols(mol_pair: (Ligand, Ligand)):
    """Get the relevant molecules from a pair of Ligand objects."""
    mol1, mol2 = mol_pair
    mol1_oe = mol1.to_oemol()
    mol2_oe = mol2.to_oemol()
    mol1_rdkit = mol1.to_rdkit()
    mol2_rdkit = mol2.to_rdkit()
    name1 = mol1.compound_name
    name2 = mol2.compound_name

    return mol1_oe, mol2_oe, mol1_rdkit, mol2_rdkit, name1, name2


def calculate_similarities(mol_pair: (Ligand, Ligand), settings: Settings = Settings()):
    """Calculate all similarity metrics for a pair of molecules."""
    lig1, lig2 = mol_pair
    mol1_oe, mol2_oe, mol1_rdkit, mol2_rdkit, name1, name2 = get_relevant_mols(mol_pair)

    return_dict = {}
    try:
        if settings.ECFP_Tanimoto:
            # ECFP4 Tanimoto
            fp1 = get_fp(
                mol1_oe, bit_size=settings.ECFP_BitSize, radius=settings.ECFP_Radius
            )
            fp2 = get_fp(
                mol2_oe, bit_size=settings.ECFP_BitSize, radius=settings.ECFP_Radius
            )
            ecfp4_sim = calculate_tanimoto(fp1, fp2)
            return_dict["ECFP4_Tanimoto"] = ecfp4_sim
            return_dict["Fingerprint"] = settings.Fingerprint

        if settings.OETanimotoCombo:
            # OpenEye TanimotoCombo
            tanimoto_combo = calculate_tanimoto_combo(mol1_oe, mol2_oe)
            return_dict["TanimotoCombo"] = tanimoto_combo

        if settings.MCS_Tanimoto:
            # MCS Analysis
            mcs = FindMCS([mol1_rdkit, mol2_rdkit])
            mcs_mol = Chem.MolFromSmarts(mcs.smartsString)
            n_mcs_atoms = mcs_mol.GetNumAtoms()
            total_atoms = (
                mol1_rdkit.GetNumAtoms() + mol2_rdkit.GetNumAtoms() - n_mcs_atoms
            )
            mcs_tanimoto = n_mcs_atoms / total_atoms if total_atoms > 0 else 0
            return_dict["MCS_NumAtoms"] = n_mcs_atoms
            return_dict["MCS_Tanimoto"] = mcs_tanimoto

        return return_dict
    except Exception as e:
        print(f"Error processing pair {name1}-{name2}: {str(e)}")
        return None


def main():

    args = parse_args()

    # make output dir
    output_dir = args.output_dir
    output_dir.mkdir(exist_ok=True, parents=True)

    # Create or load settings
    if args.settings:
        settings = Settings.load(args.settings)
    else:
        settings = Settings()
        settings.save(args.output_dir / "settings.json")

    # Use number of CPU cores if n_processes not specified
    n_processes = args.n_processes
    if n_processes is None:
        n_processes = mp.cpu_count()

    print("Loading molecules...")
    # load from file
    references = MolFileFactory(filename=args.ref_ligand_sdf).load()

    if args.query_ligand_sdf:
        queries = MolFileFactory(filename=args.query_ligand_sdf).load()
    else:
        queries = references.copy()

    # Create all pairs
    print("Creating molecule pairs...")
    all_pairs = list(itertools.product(references, queries))
    total_pairs = len(all_pairs)
    print(f"Total pairs to process: {total_pairs}")

    # Use partial function
    calculate_similarities_partial = partial(calculate_similarities, settings=settings)
    results = []
    failed_pairs = []

    # Process pairs using Pebble
    with ProcessPool(max_workers=n_processes) as pool:
        # Create iterator of futures
        future_results = pool.map(
            calculate_similarities_partial, all_pairs, timeout=args.timeout
        )

        # Process results with progress bar
        with tqdm(total=total_pairs) as pbar:
            try:
                for result in future_results:
                    if result is not None:
                        results.append(result)
                    pbar.update(1)
            except TimeoutError as error:
                failed_pairs.append(error.args[1])
                print(f"\nFunction timed out for pair {error.args[1]}")
            except Exception as error:
                print(f"\nFunction raised {error}")

    # Convert results to DataFrame
    df = pd.DataFrame(results)

    # Save results
    df.to_csv(output_dir / "chemical_similarities.csv", index=False)
    print(f"\nResults saved to {output_dir}")

    if failed_pairs:
        print(f"\nNumber of failed pairs: {len(failed_pairs)}")


if __name__ == "__main__":
    main()
