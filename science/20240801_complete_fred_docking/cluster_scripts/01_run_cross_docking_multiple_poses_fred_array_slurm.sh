#!/bin/bash
#SBATCH --job-name=fred_multiple_poses
#SBATCH --output=logs/fred_%A_%a.out
#SBATCH --error=logs/fred_%A_%a.stderr
#SBATCH --ntasks=8
#SBATCH --partition=cpu
#SBATCH --mem=24G
#SBATCH --time=24:00:00
#SBATCH --array=1-205  # Array jobs range (for jobs 1 through 205)

# Load your environment (adjust as needed)
source ~/.bashrc
conda activate asap2025

echo "Start"
# network device info
ifconfig
# dask info
dask info versions
ulimit -c 0

# Perform docking with the appropriate ligand based on SLURM_ARRAY_TASK_ID
asap-docking cross-docking \
  --target SARS-CoV-2-Mpro \
  --use-omega \
  --omega-dense \
  --allow-retries \
  --allow-final-clash \
  --posit-method FRED \
  --structure-selector PairwiseSelector \
  --fragalysis-dir /data/chodera/asap-datasets/mpro_fragalysis-04-01-24_p_series \
  --ligands "/data/chodera/asap-datasets/mpro_fragalysis-04-01-24_curated_cache/combined_split_2d/${SLURM_ARRAY_TASK_ID}.sdf" \
  --cache-dir /data/chodera/asap-datasets/mpro_fragalysis-04-01-24_curated_cache_p_series \
  --output-dir "/lila/data/chodera/asap-datasets/retro_docking/sars_fragalysis_retrospective/20241018_fred_docking/${SLURM_ARRAY_TASK_ID}" \
  --no-overwrite \
  --no-save-to-cache \
  --use-only-cache \
  --num-poses 50 \
  --use-dask \
  --dask-type local

echo "Done"
date
