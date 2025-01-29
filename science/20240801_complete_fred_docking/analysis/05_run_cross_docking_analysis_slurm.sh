#!/bin/bash
#SBATCH --job-name=cross_docking_analysis
#SBATCH --output=logs/cross_docking_analysis_%A_%a.out
#SBATCH --error=logs/cross_docking_analysis_%A_%a.out
#SBATCH --cpus-per-task 64
#SBATCH --partition=cpu
#SBATCH --mem=128GB
#SBATCH --time=2:00:00

source ~/.bashrc
conda activate harbor

echo Start
date
# network device info
ulimit -c 0

python3 05_run_cross_docking_analysis.py \
--input /data1/choderaj/paynea/asap-datasets/20250113_fred_docking/rmsd_csvs/20250122_combined_results_with_data.csv \
--output /data1/choderaj/paynea/asap-datasets/20250113_fred_docking/analyzed_data/ \
--n_cpus 64

date
echo Done
