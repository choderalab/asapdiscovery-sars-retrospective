#!/bin/bash
## Example usage:
#SBATCH --job-name="fragalysis_prep"
#SBATCH --output="logs/fragalysis_prep.out"
#SBATCH --error="logs/fragalysis_prep.stderr"
#SBATCH --ntasks=64
#SBATCH --partition=cpuqueue
#SBATCH --mem=2GB
#SBATCH --time=02:00:00

# Activate conda environment
source ~/.bashrc
conda activate asap2025

echo "Start"
# Network device info
ifconfig
# Dask info
dask info versions
ulimit -c 0

# Run ASAP CLI
asap-cli protein-prep \
  --target SARS-CoV-2-Mpro \
  --fragalysis-dir /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_p_series \
  --cache-dir /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_p_series_cache_20250110 \
  --output-dir fragalysis_prep_out \
  --loop-db /data1/choderaj/asap-playground/rcsb_spruce.loop_db \
  --save-to-cache \
  --ref-chain A \
  --active-site-chain A \

echo "Done"
date
