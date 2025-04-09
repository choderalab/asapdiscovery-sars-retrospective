#!/bin/bash
#SBATCH --job-name=run_evaluators_scafold_date_split_x_to_y
#SBATCH --output=logs/run_evaluators_scafold_date_split_x_to_y_%A_%a.out
#SBATCH --error=logs/run_evaluators_scafold_date_split_x_to_y_%A_%a.err
#SBATCH --cpus-per-task 1
#SBATCH --partition=cpu
#SBATCH --mem=16GB
#SBATCH --time=0:10:00
#SBATCH --array=0-2 #822 #4

source ~/.bashrc
conda activate harbor

echo Start
date

data_dir='/data1/choderaj/paynea/asap-datasets/20250212_p_to_x_posit'

# Number of files to process per job
FILES_PER_JOB=10

# Calculate the starting and ending file numbers for this job
START_FILE=$((SLURM_ARRAY_TASK_ID * FILES_PER_JOB + 1))
END_FILE=$((START_FILE + FILES_PER_JOB - 1))

# Make sure we don't exceed the total number of files
if [ $END_FILE -gt $TOTAL_FILES ]; then
    END_FILE=$TOTAL_FILES
fi

echo "Processing files $START_FILE to $END_FILE (Job array ID: $SLURM_ARRAY_TASK_ID)"

# Loop through the files assigned to this job
for FILE_NUM in $(seq $START_FILE $END_FILE); do
  FORMATTED_NUM=$(printf "%0d" $FILE_NUM)
  FILE_NAME="$data_dir/scaffold_split_x_to_y/evaluator_settings_scaffold_split_x_to_y_${FORMATTED_NUM}.json"
  echo Running $FILE_NAME
  python3 08_run_evaluators.py \
  --input $data_dir/combined_results/20250311_combined_results \
  --output $data_dir/scaffold_split_x_to_y \
  --n-cpus 1 \
  --job-id $SLURM_ARRAY_TASK_ID \
  --evaluator-json $FILE_NAME
done

date
echo Done