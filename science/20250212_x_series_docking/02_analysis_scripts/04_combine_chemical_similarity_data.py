"""
Takes the previously calculated chemical similarity data and outputs a CSV file with the rest of the docking results
"""

import pandas as pd
import argparse
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Combine all relevant data for analysis"
    )

    # add any number of csv files
    parser.add_argument("data_csvs", nargs="+")
    return parser.parse_args()


def main():
    args = parse_args()
    dfs = []
    for csv in args.csvs:
        dfs.append(pd.read_csv(csv))
    df = pd.concat(dfs)
    df.to_csv("combined_data.csv", index=False)
