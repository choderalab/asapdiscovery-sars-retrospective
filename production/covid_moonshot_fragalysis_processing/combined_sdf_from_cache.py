"""
This script generates a combined 2D SDF file from a cache of moonshot data.
"""

from pathlib import Path
from asapdiscovery.modeling.protein_prep import ProteinPrepper
from asapdiscovery.data.schema.ligand import Ligand, write_ligands_to_multi_sdf
import argparse
from asapdiscovery.data.util.logging import FileLogger


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input_cache",
        type=Path,
        help="Path to input cache generated by the asapdiscovery-data package",
    )
    parser.add_argument(
        "--flatten",
        action="store_true",
        help="If true, will flatten the molecules before saving them. "
        "This is useful if the molecules have 3D coordinates but you want to save them as 2D",
    )
    parser.add_argument("-o", "--output_dir", type=Path, help="Path to output path")
    return parser.parse_args()


def main():
    args = get_args()
    data_dir = args.input_cache
    output_dir = args.output_dir

    complexes = ProteinPrepper.load_cache(data_dir)
    logger = FileLogger(
        "combine_sdfs", output_dir, logfile="combine_sdfs.log"
    ).getLogger()
    logger.info(f"Found {len(complexes)} complexes in the cache: '{data_dir}'")
    if args.flatten:
        logger.info("Flattening the molecules before saving them")
        ligands = [
            Ligand.from_smiles(
                complex.ligand.smiles,
                tags=complex.ligand.tags,
                compound_name=complex.ligand.compound_name,
                ids=complex.ligand.ids,
            )
            for complex in complexes
        ]
    else:
        ligands = [complex.ligand for complex in complexes]
    out_name = f"combined_2d.sdf" if args.flatten else "combined_3d.sdf"
    write_ligands_to_multi_sdf(output_dir / out_name, ligands)
    logger.info(f"Combined {len(ligands)} ligands into {output_dir / out_name}")


if __name__ == "__main__":
    main()