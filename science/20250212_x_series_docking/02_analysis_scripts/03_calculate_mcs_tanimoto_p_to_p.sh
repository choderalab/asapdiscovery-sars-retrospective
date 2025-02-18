#!/bin/bash
#SBATCH --job-name=calculate_mcs_tanimoto
#SBATCH --output=logs/calculate_mcs_tanimoto.out
#SBATCH --error=logs/calculate_mcs_tanimoto.err
#SBATCH --partition=cpu
#SBATCH --mem=64GB
#SBATCH --time=02:00:00
source ~/.bashrc
mamba activate asap2025e
python3 03_calculate_mcs_tanimoto.py \
--ref-ligand-sdf /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_p_series_curated_cache_20250113/ligand_files_20250113/combined_3d.sdf \
--output-dir /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_p_series_curated_cache_20250113/ligand_files_20250113/mcs_tanimoto
