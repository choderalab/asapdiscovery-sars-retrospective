#!/bin/bash
#SBATCH --job-name=combine_scafold_date_split_results
#SBATCH --output=logs/combine_scafold_date_split_results.out
#SBATCH --error=logs/combine_scafold_date_split_results.err
#SBATCH --cpus-per-task 1
#SBATCH --partition=cpu
#SBATCH --mem=16GB
#SBATCH --time=0:30:00

source ~/.bashrc
conda activate harbor

echo Start
date

data_dir='/data1/choderaj/paynea/asap-datasets/20250212_p_to_x_posit/scaffold_split'

python combine_date_split_results.py -i $data_dir -o "$data_dir"/combined_results.csv -p "*/*.csv"

date
echo Done