#!/bin/bash
#SBATCH --job-name=cross_docking_analysis
#SBATCH --output=logs/cross_docking_analysis_%A.out
#SBATCH --error=logs/cross_docking_analysis_%A.out
#SBATCH --cpus-per-task 32
#SBATCH --partition=cpu
#SBATCH --mem=128GB
#SBATCH --time=4:00:00

source ~/.bashrc
conda activate harbor

echo Start
date
# network device info
ulimit -c 0

python3 06_run_cross_docking_analysis.py \
--input /data1/choderaj/paynea/asap-datasets/20250212_p_to_x_posit/rmsd_csvs/20250217_combined_results_with_data.csv \
--output /data1/choderaj/paynea/asap-datasets/20250212_p_to_x_posit/analyzed_data \
--date_dict_path /data1/choderaj/paynea/asapdiscovery-sars-retrospective/data/cmpd_date_dict/date_dict.json \
--n_cpus 32

date
echo Done
