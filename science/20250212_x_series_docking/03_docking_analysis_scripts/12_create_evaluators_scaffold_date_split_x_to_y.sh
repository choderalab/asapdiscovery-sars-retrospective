#!/bin/bash
#SBATCH --job-name=create_evaluators_scafold_date_split_x_to_y
#SBATCH --output=logs/create_evaluators_scafold_date_split_x_to_y.out
#SBATCH --error=logs/create_evaluators_scafold_date_split_x_to_y.err
#SBATCH --cpus-per-task 1
#SBATCH --partition=cpu
#SBATCH --mem=32GB
#SBATCH --time=0:00:10

source ~/.bashrc
conda activate harbor

echo Start
date
# network device info
ulimit -c 0

data_dir='/data1/choderaj/paynea/asap-datasets/20250212_p_to_x_posit'

python3 09_create_evaluators_v2.py \
--input $data_dir/combined_results/20250311_combined_results \
--output $data_dir/scaffold_split \
--settings 'settings_scaffold_split_x_to_y.yml' \

date
echo Done