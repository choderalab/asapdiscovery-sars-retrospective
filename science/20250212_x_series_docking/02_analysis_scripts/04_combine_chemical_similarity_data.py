"""
Takes the previously calculated chemical similarity data and outputs a CSV file with the rest of the docking results
"""
import pandas as pd
import argparse
from pathlib import Path


def parse_args():
