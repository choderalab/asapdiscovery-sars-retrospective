#!/bin/bash
#SBATCH --job-name=run_evaluators
#SBATCH --output=logs/run_evaluators_%A_%a.out
#SBATCH --error=logs/run_evaluators_%A_%a.err
#SBATCH --cpus-per-task 4
#SBATCH --partition=cpu
#SBATCH --mem=16GB
#SBATCH --time=0:30:00
#SBATCH --array=0-9

source ~/.bashrc
conda activate harbor

echo Start
date


python3 run_evaluators.py \
--input /data1/choderaj/paynea/asap-datasets/20250212_p_to_x_fred/rmsd_csvs/20250217_combined_results_with_data.csv \
--output /data1/choderaj/paynea/asap-datasets/20250212_p_to_x_fred/test_run_evaluators \
--n-cpus 4 \
--job-id $SLURM_ARRAY_TASK_ID \
--evaluator-json /data1/choderaj/paynea/asap-datasets/20250212_p_to_x_fred/test_evaluator_creation/evaluator_*"${SLURM_ARRAY_TASK_ID}".json

date
echo Done
