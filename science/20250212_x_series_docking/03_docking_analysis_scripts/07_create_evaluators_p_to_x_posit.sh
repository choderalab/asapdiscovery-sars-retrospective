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

data_dir='/data1/choderaj/paynea/asap-datasets/20250212_p_to_x_posit'

python3 07_create_evaluators.py \
--input $data_dir/combined_results/20250311_combined_results \
--output $data_dir/datesplit \
--settings 'settings_cross_docking_defaults.yml' \
--update-n-per-split

python3 07_create_evaluators.py \
--input $data_dir/combined_results/20250311_combined_results \
--output $data_dir/similarity_split \
--settings 'settings_similarity_split_tanimotocombo.yml'

python3 07_create_evaluators.py \
--input $data_dir/combined_results/20250311_combined_results \
--output $data_dir/scaffold_split \
--settings 'settings_scaffold_split_not_x_to_x.yml' \
'settings_scaffold_split_x_to_not_x.yml'

date
echo Done
