#!/bin/bash
#SBATCH --job-name=run_evaluators_multipose_split
#SBATCH --output=logs/run_evaluators_multipose_split%a.out
#SBATCH --error=logs/run_evaluators_multipose_split%a.err
#SBATCH --cpus-per-task 1
#SBATCH --partition=cpu
#SBATCH --mem=32GB
#SBATCH --time=0:30:00
#SBATCH --array=0-432

source ~/.bashrc
conda activate harbor

echo Start
date

data_dir='/data1/choderaj/paynea/asap-datasets/20250212_p_to_x_posit'

# Total number of files to process
TOTAL_FILES=432

# Number of files to process per job
FILES_PER_JOB=1

# Calculate the starting and ending file numbers for this job, starting at 0
START_FILE=$((SLURM_ARRAY_TASK_ID * FILES_PER_JOB))
END_FILE=$((START_FILE + FILES_PER_JOB - 1))

# Make sure we don't exceed the total number of files
if [ $END_FILE -gt $TOTAL_FILES ]; then
    END_FILE=$TOTAL_FILES
fi

# Collect the file names in a list
evaluator_files=""
for FILE_NUM in $(seq $START_FILE $END_FILE); do
  FORMATTED_NUM=$(printf "%0d" $FILE_NUM)
  FILE_NAME="$data_dir/multipose_split/evaluator_settings_multipose_split_${FORMATTED_NUM}.json"
  evaluator_files="$evaluator_files $FILE_NAME"
done

# Pass the collected files to the --evaluator-json argument
python3 08_run_evaluators.py \
--input $data_dir/combined_results/20250311_combined_results \
--output $data_dir/multipose_split \
--n-cpus $FILES_PER_JOB \
--job-id $SLURM_ARRAY_TASK_ID \
--evaluator-json $evaluator_files

date
echo Done