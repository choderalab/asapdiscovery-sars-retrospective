#!/bin/bash
#SBATCH --job-name=run_evaluators_scafold_date_split_x_to_y
#SBATCH --output=logs/run_evaluators_scafold_date_split_x_to_y_%A_%a.out
#SBATCH --error=logs/run_evaluators_scafold_date_split_x_to_y_%A_%a.err
#SBATCH --cpus-per-task 1
#SBATCH --partition=cpu
#SBATCH --mem=4GB
#SBATCH --time=0:10:00
#SBATCH --array=0-28224

source ~/.bashrc
conda activate harbor

echo Start
date

data_dir='/data1/choderaj/paynea/asap-datasets/20250212_p_to_x_posit'

python3 08_run_evaluators.py \
--input $data_dir/combined_results/20250311_combined_results \
--output $data_dir/scaffold_split_x_to_y \
--n-cpus 1 \
--job-id $SLURM_ARRAY_TASK_ID \
--evaluator-json $data_dir/scaffold_split/evaluator_*_x_to_y_*"${SLURM_ARRAY_TASK_ID}".json


date
echo Done