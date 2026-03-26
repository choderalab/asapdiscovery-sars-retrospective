#!/bin/bash
#SBATCH --job-name=run_evaluators
#SBATCH --output=logs/run_evaluators_%A_%a.out
#SBATCH --error=logs/run_evaluators_%A_%a.err
#SBATCH --cpus-per-task 8
#SBATCH --partition=cpu
#SBATCH --mem=16GB
#SBATCH --time=2:00:00
#SBATCH --array=0-9

source ~/.bashrc
conda activate harbor

echo Start
date

data_dir='/data1/choderaj/paynea/asap-datasets/20250212_p_to_x_posit'

#python3 08_run_evaluators.py \
#--input $data_dir/combined_results/20250311_combined_results \
#--output $data_dir/similarity_split \
#--n-cpus 4 \
#--job-id $SLURM_ARRAY_TASK_ID \
#--evaluator-json $data_dir/similarity_split/evaluator_*"${SLURM_ARRAY_TASK_ID}".json

python3 08_run_evaluators.py \
--input $data_dir/combined_results/20250311_combined_results \
--output $data_dir/scaffold_split \
--n-cpus 8 \
--job-id $SLURM_ARRAY_TASK_ID \
--evaluator-json $data_dir/scaffold_split/evaluator_*"${SLURM_ARRAY_TASK_ID}".json


date
echo Done
