"""
Script to generate chemical similarity analysis between reference and query ligands in a docking experiment.
"""

from rdkit import Chem
from rdkit.Chem.rdFMCS import FindMCS
from asapdiscovery.data.backend.openeye import oechem, oeshape
from openeye import oegraphsim
from asapdiscovery.data.readers.molfile import MolFileFactory
from asapdiscovery.data.schema.ligand import Ligand
import pandas as pd
import itertools
import argparse
from pebble import ProcessPool
from concurrent.futures import TimeoutError
import multiprocessing as mp
from pathlib import Path
from pydantic import BaseSettings, BaseModel
import json
from functools import partial
import time
from datetime import datetime
import pickle
from asapdiscovery.data.util.logging import FileLogger


class LigandPair(BaseModel):
    """Class to represent a pair of ligands."""

    ref_ligand: Ligand
    query_ligand: Ligand

    @property
    def unique_name(self):
        return f"{self.ref_ligand.compound_name}_{self.query_ligand.compound_name}"

    def __eq__(self, other):
        if not isinstance(other, LigandPair):
            return False
        return (
            self.ref_ligand == other.ref_ligand
            and self.query_ligand == other.query_ligand
        )

    def __hash__(self):
        return hash((self.ref_ligand, self.query_ligand))

    def __repr__(self):
        return f"LigandPair(ref_ligand={self.ref_ligand.compound_name}, query_ligand={self.query_ligand.compound_name})"

    def to_tuple(self):
        return (self.ref_ligand, self.query_ligand)

    @classmethod
    def from_tuple(cls, pair: tuple[Ligand, Ligand]):
        return cls(ref_ligand=pair[0], query_ligand=pair[1])


class Settings(BaseSettings):
    ECFP_Tanimoto: bool = True
    ECFP_Radius: int = 2
    ECFP_BitSize: int = 2048
    OETanimotoCombo: bool = False
    MCS_Tanimoto: bool = True
    batch_size: int = 1000
    cache_frequency: int = 5000  # Save cache every N pairs
    report_frequency: int = 1000  # Report progress every N pairs

    @property
    def Fingerprint(self):
        return f"ECFP{self.ECFP_Radius * 2}_{self.ECFP_BitSize}"

    def save(self, path):
        with open(path, "w") as f:
            f.write(self.json(indent=4))

    @classmethod
    def load(cls, path):
        with open(path, "r") as f:
            return cls(**json.load(f))


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
        help="Path to directory containing prepped query ligand sdf. If false, ref-ligand-sdf will be used.",
    )
    parser.add_argument(
        "--settings", type=Path, required=False, help="Path to settings json file"
    )
    parser.add_argument("--test-n", type=int, default=-1, help="Test n pairs")
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
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from last cached state",
    )
    return parser.parse_args()


# Your existing similarity calculation functions here...


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


def get_relevant_mols(mol_pair: LigandPair):
    """Get the relevant molecules from a pair of Ligand objects."""
    mol1, mol2 = mol_pair.to_tuple()
    mol1_oe = mol1.to_oemol()
    mol2_oe = mol2.to_oemol()
    mol1_rdkit = mol1.to_rdkit()
    mol2_rdkit = mol2.to_rdkit()
    name1 = mol1.compound_name
    name2 = mol2.compound_name

    return mol1_oe, mol2_oe, mol1_rdkit, mol2_rdkit, name1, name2


def calculate_similarities(mol_pair: (Ligand, Ligand), settings: Settings):
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


class ProcessingState:
    """Class to track processing state and handle caching"""

    def __init__(self, output_dir: Path, total_pairs: int, settings: Settings, logger):
        self.output_dir = output_dir
        self.total_pairs = total_pairs
        self.settings = settings
        self.results = []
        self.failed_pairs = []
        self.processed_pairs = 0
        self.start_time = time.time()
        self.cache_path = output_dir / "processing_cache.pkl"
        self.last_cache_time = time.time()
        self.logger = logger

    def add_result(self, result):
        """Add a result and update progress"""
        if result is not None:
            self.results.append(result)
        self.processed_pairs += 1
        self._update_progress()
        self._maybe_cache()

    def add_failed(self, pair: LigandPair):
        """Add a failed pair"""
        self.failed_pairs.append(pair)
        self.processed_pairs += 1
        self._update_progress()
        self._maybe_cache()

    def _update_progress(self):
        """Update progress display"""
        if (
            self.processed_pairs % self.settings.report_frequency == 0
        ):  # Update every 10 pairs
            elapsed = time.time() - self.start_time
            pairs_per_second = self.processed_pairs / elapsed
            remaining_pairs = self.total_pairs - self.processed_pairs
            eta_seconds = (
                remaining_pairs / pairs_per_second if pairs_per_second > 0 else 0
            )

            self.logger.info(
                f"Progress: {self.processed_pairs}/{self.total_pairs} "
                f"({(self.processed_pairs / self.total_pairs * 100):.1f}%) | "
                f"Speed: {pairs_per_second:.1f} pairs/s | "
                f"ETA: {datetime.fromtimestamp(time.time() + eta_seconds).strftime('%H:%M:%S')}"
            )

    def _maybe_cache(self):
        """Cache results if enough time has passed or enough pairs processed"""
        if (
            self.processed_pairs % self.settings.cache_frequency == 0
            or time.time() - self.last_cache_time > 300
        ):  # Cache every 5 minutes
            self.save_cache()

    def save_cache(self):
        """Save current state to cache"""
        cache_data = {
            "results": self.results,
            "failed_pairs": self.failed_pairs,
            "processed_pairs": self.processed_pairs,
            "start_time": self.start_time,
        }
        with open(self.cache_path, "wb") as f:
            pickle.dump(cache_data, f)
        self.last_cache_time = time.time()
        self.logger.info(f"Cached progress at {self.processed_pairs} pairs")

    @classmethod
    def load_cache(cls, output_dir: Path, total_pairs: int, settings: Settings, logger):
        """Load state from cache"""
        cache_path = output_dir / "processing_cache.pkl"
        if not cache_path.exists():
            return cls(output_dir, total_pairs, settings)

        with open(cache_path, "rb") as f:
            cache_data = pickle.load(f)

        state = cls(output_dir, total_pairs, settings)
        state.results = cache_data["results"]
        state.failed_pairs = cache_data["failed_pairs"]
        state.processed_pairs = cache_data["processed_pairs"]
        state.start_time = cache_data["start_time"]

        logger.info(f"Resumed from cache at {state.processed_pairs} pairs")
        return state


def process_batch(batch, settings: Settings, logger):
    """Process a batch of molecule pairs"""
    calculate_similarities_partial = partial(calculate_similarities, settings=settings)
    batch_results = []

    for pair in batch:
        try:
            result = calculate_similarities_partial(pair)
            if result is not None:
                batch_results.append(result)
        except Exception as e:
            logger.error(f"Error processing pair: {str(e)}")

    return batch_results


def main():
    args = parse_args()
    output_dir = args.output_dir
    output_dir.mkdir(exist_ok=True, parents=True)

    # Create or load settings
    if args.settings:
        settings = Settings.load(args.settings)
    else:
        settings = Settings()
        settings.save(output_dir / "settings.json")

    # Use number of CPU cores if n_processes not specified
    n_processes = args.n_processes or mp.cpu_count()

    logger = FileLogger(
        "run_chemical_similarity_analysis",
        output_dir,
        logfile="run_chemical_similarity_analysis.log",
    ).getLogger()

    logger.info("Loading molecules...")
    references = MolFileFactory(filename=args.ref_ligand_sdf).load()
    queries = (
        MolFileFactory(filename=args.query_ligand_sdf).load()
        if args.query_ligand_sdf
        else references.copy()
    )

    # Create all pairs
    all_pairs = [
        LigandPair(ref_ligand=ref, query_ligand=query)
        for ref, query in itertools.product(references, queries)
    ]
    total_pairs = len(all_pairs)
    logger.info(f"Total pairs to process: {total_pairs}")

    if args.test_n > 0:
        all_pairs = all_pairs[: args.test_n]
        total_pairs = len(all_pairs)
        logger.info(f"Testing on {total_pairs} pairs")

    # Initialize or load state
    if args.resume and (output_dir / "processing_cache.pkl").exists():
        state = ProcessingState.load_cache(
            output_dir, total_pairs, settings=settings, logger=logger
        )
        # Skip already processed pairs
        all_pairs = all_pairs[state.processed_pairs :]
    else:
        state = ProcessingState(
            output_dir, total_pairs, settings=settings, logger=logger
        )

    # Use partial
    process_batch_partial = partial(process_batch, settings=settings, logger=logger)
    logger.info("Starting processing...")

    # Process in batches
    for i in range(0, len(all_pairs), settings.batch_size):
        batch = all_pairs[i : i + settings.batch_size]

        with ProcessPool(max_workers=n_processes) as pool:
            future = pool.schedule(
                process_batch_partial, batch, timeout=args.timeout * len(batch)
            )

            try:
                logger.info(f"Processing batch {i // settings.batch_size}")
                batch_results = future.result()
                for result in batch_results:
                    state.add_result(result)
            except TimeoutError:
                logger.error(f"Batch {i // settings.batch_size} timed out")
                for pair in batch:
                    state.add_failed(pair)
            except Exception as e:
                logger.error(f"Error processing batch: {str(e)}")
                for pair in batch:
                    state.add_failed(pair)

    # Save final results
    df = pd.DataFrame(state.results)
    df.to_csv(output_dir / "chemical_similarities.csv", index=False)

    # Save failed pairs
    if state.failed_pairs:
        with open(output_dir / "failed_pairs.json", "a") as f:
            json.dump([ligpair.json() for ligpair in state.failed_pairs], f)
        logger.info(f"\nNumber of failed pairs: {len(state.failed_pairs)}")

    logger.info(f"Results saved to {output_dir}")
    logger.info(f"Total processing time: {time.time() - state.start_time:.1f} seconds")


if __name__ == "__main__":
    main()
