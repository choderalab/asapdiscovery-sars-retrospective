#!/bin/bash
#SBATCH --job-name=calculate_rmsd
#SBATCH --output=logs/calculate_rmsd_%A_%a.out
#SBATCH --error=logs/calculate_rmsd_%A_%a.out
#SBATCH --cpus-per-task 6
#SBATCH --partition=cpu
#SBATCH --mem=128GB
#SBATCH --time=2:00:00
#SBATCH --array=1-218  # Array jobs range (for jobs 1 through n)

# Load your environment (adjust as needed)
source ~/.bashrc
conda activate asap2025e

# don't forget to use the 3d ligands instead of the 2d
python3.10 03_calculate_rmsd_from_docking_results.py \
-d "/data1/choderaj/paynea/asap-datasets/20250113_fred_docking/${SLURM_ARRAY_TASK_ID}" \
-l "/data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_p_series_curated_cache_20250113/ligand_files_20250113/split_3d/${SLURM_ARRAY_TASK_ID}.sdf" \
-o "/data1/choderaj/paynea/asap-datasets/20250113_fred_docking/rmsc_csvs/${SLURM_ARRAY_TASK_ID}.csv"

echo Done
date
