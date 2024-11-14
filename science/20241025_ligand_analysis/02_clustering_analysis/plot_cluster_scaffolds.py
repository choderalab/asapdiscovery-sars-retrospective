"""
The purpose of this script is to plot the top 96 scaffolds in the cluster.
"""

import argparse
from pathlib import Path
import pandas as pd
from asapdiscovery.data.schema.ligand import Ligand
from rdkit import Chem


def parse_args():
    parser = argparse.ArgumentParser(description="Plot cluster scaffolds")
    parser.add_argument("--input_csv", type=Path, help="Path to the input CSV file")
    parser.add_argument("--output_dir", type=Path, help="Path to the output directory")
    parser.add_argument(
        "--compound_data_csv", type=Path, help="Path to the compound data csv"
    )
    return parser.parse_args()


def convert_df_to_scaffold_list(df):
    cluster_types = df["cluster_type"].unique()
    counts = df.groupby("cluster_id").count()["compound_name"].to_list()
    cluster_ids = df["cluster_id"].unique()
    scaffolds = df["scaffold_smarts"].unique()

    return_dict = {}
    for cluster_type in cluster_types:
        scaffold_list = []
        for scaffold, cluster_id, count in zip(scaffolds, cluster_ids, counts):
            try:
                scaffold_list.append(
                    Ligand.from_smiles(
                        scaffold,
                        compound_name=f"Cluster {cluster_id} - {count} molecules",
                    )
                )
            except Exception as e:
                print(
                    f"Failed to generate Ligand for cluster {cluster_id} ({scaffold}) with {count} molecules"
                )
        return_dict[cluster_type] = scaffold_list
    return return_dict


def draw_scaffolds(
    scaffold_list: list[Ligand], first_n=-1, mols_per_row=-1, use_svg=True
):
    from rdkit.Chem import Draw, rdDepictor

    scaffold_rdmols = [Chem.RemoveHs(ligand.to_rdkit()) for ligand in scaffold_list]

    # Set Draw Options
    dopts = Draw.rdMolDraw2D.MolDrawOptions()
    dopts.setHighlightColour((68 / 256, 178 / 256, 212 / 256))
    dopts.highlightBondWidthMultiplier = 16
    d2d = Draw.MolDraw2DCairo(350, 300)
    print("Preparing depictions")
    for mol in scaffold_rdmols[:first_n]:
        Draw.MolToImage(mol, size=(200, 200), options=dopts)
        rdDepictor.Compute2DCoords(mol)
        rdDepictor.StraightenDepiction(mol)
        d2d.DrawMolecule(mol)
    print("Creating image")
    img = Draw.MolsToGridImage(
        scaffold_rdmols[:first_n],
        molsPerRow=mols_per_row,
        subImgSize=(200, 200),
        useSVG=use_svg,
        legends=[ligand.compound_name for ligand in scaffold_list[:first_n]],
        drawOptions=dopts,
    )
    return img


def main():
    args = parse_args()
    input_csv = args.input_csv
    output_dir = args.output_dir
    compound_data_csv = args.compound_data_csv

    compound_data = pd.read_csv(compound_data_csv)

    df = pd.read_csv(input_csv)

    df = df.merge(compound_data, on="compound_name", how="left")

    scaffold_list_dict = convert_df_to_scaffold_list(df)

    for cluster_type, scaffold_list in scaffold_list_dict.items():
        print(f"Plotting {cluster_type}")
        for use_svg in [True, False]:
            img = draw_scaffolds(
                scaffold_list, first_n=96, mols_per_row=8, use_svg=use_svg
            )
            if use_svg:
                with open(
                    output_dir / f"{cluster_type}_scaffold_images_8x12.svg", "w"
                ) as f:
                    f.write(img)
            else:
                img.save(output_dir / f"{cluster_type}_scaffold_images_8x12.png")


if __name__ == "__main__":
    main()
