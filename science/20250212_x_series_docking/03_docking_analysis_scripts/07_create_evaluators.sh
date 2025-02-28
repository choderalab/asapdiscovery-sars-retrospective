#!/bin/bash
#SBATCH --job-name=create_evaluators
#SBATCH --output=logs/create_evaluators_%A.out
#SBATCH --error=logs/create_evaluators_%A.err
#SBATCH --cpus-per-task 1
#SBATCH --partition=cpu
#SBATCH --mem=4GB
#SBATCH --time=0:00:10

source ~/.bashrc
conda activate harbor

echo Start
date
# network device info
ulimit -c 0

python3 create_evaluators.py \
--input /data1/choderaj/paynea/asap-datasets/20250212_p_to_x_posit/rmsd_csvs/20250217_combined_results_with_data.csv \
--output /data1/choderaj/paynea/asap-datasets/20250212_p_to_x_posit/test_evaluator_creation \
--settings 'settings_cross_docking_defaults.yml' \
--update-n-per-split

date
echo Done
