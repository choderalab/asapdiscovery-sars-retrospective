#!/bin/bash
#SBATCH --job-name=run_bemis_murcko_clustering
#SBATCH --output=logs/run_bemis_murcko_clustering.out
#SBATCH --error=logs/run_bemis_murcko_clustering.err
#SBATCH --partition=cpu
#SBATCH --cpus-per-task=1
#SBATCH --mem=64GB
#SBATCH --time=02:00:00
source ~/.bashrc
mamba activate asap2025e
python 05_run_bemis_murcko_clustering.py \
--sdf-2d /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_x_series_active_site_cache_20250212/ligand_files_20250212/combined_2d.sdf \
/data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_p_series_curated_cache_20250113/ligand_files_20250113/combined_2d.sdf \
--output-dir /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_scaffolds_20250311
