# Copied from Ben

import click
from pathlib import Path

from asapdiscovery.data.backend.openeye import (
    load_openeye_sdfs,
    oechem,
    save_openeye_sdfs,
)


def calc_rmsd(coo1, coo2, n_atoms):
    return oechem.OERMSD(coo1, coo2, n_atoms)


def get_coords(mol):
    return oechem.OEFloatArray(
        [x for a in mol.GetAtoms() for x in mol.GetCoords()[a.GetIdx()]]
    )


@click.command()
@click.option(
    "-d",
    "--dock-dir",
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Top-level docking results directory.",
)
@click.option("-i", "--in-name", default="docked.sdf", help="File name of inputs.")
@click.option(
    "--out-dir",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, path_type=Path),
    help=(
        "Top-level output directory. Files will go in the same path as their input "
        "if this is not given."
    ),
)
@click.option(
    "-o",
    "--out-name",
    default="docked_{}_{}.sdf",
    help="File name of filtered results.",
)
@click.option(
    "-c",
    "--cutoff",
    type=float,
    default=2.0,
    help="RMSD cutoff for distinct molecules.",
)
@click.option(
    "-k",
    "--comp-key",
    default="docking-confidence-POSIT",
    help="SD data tag to use for sorting molecule.",
)
@click.option(
    "--sort-asc",
    is_flag=True,
    help="Sort molecules by ascending values instead of descending.",
)
def main(
    dock_dir: Path,
    in_name: str = "docked.sdf",
    out_dir: Path | None = None,
    out_name: str = "docked_{}_{}.sdf",
    cutoff: float = 2.0,
    comp_key: str = "docking-confidence-POSIT",
    sort_asc: bool = False,
):
    # Set up out_dir
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)
    else:
        out_dir = dock_dir

    for docked_fn in dock_dir.rglob(f"*/{in_name}"):
        # Sort molecules based on docking score/energy
        all_mols = sorted(
            load_openeye_sdfs(docked_fn),
            key=lambda mol: float(oechem.OEGetSDData(mol, comp_key)),
            reverse=not sort_asc,
        )
        n_atoms = all_mols[0].NumAtoms()
        for mol in all_mols[1:]:
            assert mol.NumAtoms() == n_atoms

        # Get coords for all mols
        all_coords = [get_coords(mol) for mol in all_mols]
        unique_mol_idx = []
        for i, coo1 in enumerate(all_coords):
            for idx in unique_mol_idx:
                coo2 = all_coords[idx]
                if calc_rmsd(coo1, coo2, n_atoms) <= cutoff:
                    # Similar to an already selected mol so don't need this one
                    break
            else:
                unique_mol_idx.append(i)

        unique_mols = [all_mols[idx] for idx in unique_mol_idx]
        out_fn = out_dir / docked_fn.parent.name / out_name.format(cutoff, comp_key)
        out_fn.parent.mkdir(parents=True, exist_ok=True)
        save_openeye_sdfs(unique_mols, out_fn)
        # print(out_fn, flush=True)


if __name__ == "__main__":
    main()
