"""This script fixes some bespoke errors with the prepped fragalysis cache"""
from pathlib import Path
from asapdiscovery.modeling.protein_prep import ProteinPrepper, PreppedComplex
from asapdiscovery.data.schema.ligand import Ligand, write_ligands_to_multi_sdf
import argparse
from asapdiscovery.data.util.logging import FileLogger
import rdkit

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input_cache",
        type=Path,
        help="Path to input cache generated by the asapdiscovery-data package.",
    )
    return parser.parse_args()

def main():
    args = get_args()
    cache = args.input_cache
    if not cache.exists():
        raise FileNotFoundError(f"Cache file {cache} not found")

    # fix ligand in P0097
    prepped_directories = cache.glob("P0097")
    for prepped_directory in prepped_directories:
        ligand = prepped_directory / "MAT-POS-5d65ec79-1.sdf"
        if not ligand.exists():
            raise FileNotFoundError(f"Ligand file {ligand} not found")
        ligand = Ligand.from_sdf(ligand)
        # get rid of 2nd ligand
        rdmol = ligand.to_rdkit()

        # delete second fragment
        frag_to_delete = [frag for frag in rdkit.Chem.GetMolFrags(rdmol)][1]
        editable = rdkit.Chem.EditableMol(rdmol)

        # need to change index as we delete
        # since the indices are already sorted, each time we delete one, the next will
        # have a lower index
        for i, idx in enumerate(frag_to_delete):
            idx = idx - i
            editable.RemoveAtom(idx)
        new_mol = editable.GetMol()
        rdkit.Chem.rdmolops.SanitizeMol(new_mol, sanitizeOps=rdkit.Chem.rdmolops.SANITIZE_ALL)
        sdf_str = rdkit.Chem.rdmolfiles.MolToMolBlock(new_mol)
        new_lig = Ligand.from_sdf_str(sdf_str, compound_name=ligand.compound_name)
        new_lig.to_sdf(prepped_directory / "MAT-POS-5d65ec79-1.sdf")

        json_file = list(prepped_directory.glob('*.json'))[0]
        prepped_complex = PreppedComplex.from_json_file(json_file)
        prepped_complex.ligand = new_lig
        prepped_complex.to_json(json_file)

if __name__ == "__main__":
    main()