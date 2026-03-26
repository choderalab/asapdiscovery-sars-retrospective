#!/bin/bash
#SBATCH --job-name=fred_multiple_poses
#SBATCH --output=logs/fred_%A_%a.out
#SBATCH --error=logs/fred_%A_%a.stderr
#SBATCH --cpus-per-task 32
#SBATCH --partition=cpu
#SBATCH --mem=256GB
#SBATCH --time=24:00:00
#SBATCH --array=1  # Array jobs range (for jobs 1 through n)

# Load your environment (adjust as needed)
source ~/.bashrc
conda activate asap2025e

echo "Start"
# network device info
ifconfig
# dask info
dask info versions
ulimit -c 0

cache=/data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_x_series_active_site_cache_20250212
ligand_files=$cache/ligand_files_20250212

# Perform docking with the appropriate ligand based on SLURM_ARRAY_TASK_ID
asap-cli docking cross-docking \
  --target SARS-CoV-2-Mpro \
  --use-omega \
  --omega-dense \
  --allow-retries \
  --allow-final-clash \
  --relax-mode clash \
  --posit-method FRED \
  --structure-selector PairwiseSelector \
  --fragalysis-dir /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_x_series_active_site \
  --ligands "/data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_p_series_curated_cache_20250113/ligand_files_20250113/split_2d/${SLURM_ARRAY_TASK_ID}.sdf" \
  --cache-dir $cache \
  --output-dir "/data1/choderaj/paynea/asap-datasets/20250212_p_to_x_fred/${SLURM_ARRAY_TASK_ID}" \
  --no-overwrite \
  --no-save-to-cache \
  --use-only-cache \
  --num-poses 50 \
  --use-dask \
  --dask-type local \
  --dask-n-workers 32

echo "Done"
date
