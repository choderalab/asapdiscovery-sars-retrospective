#!/bin/bash
#SBATCH --job-name=calculate_tanimoto_combo
#SBATCH --output=logs/calculate_tanimoto_combo.out
#SBATCH --error=logs/calculate_tanimoto_combo.err
#SBATCH --partition=cpu
#SBATCH --cpus-per-task=32
#SBATCH --mem=64GB
#SBATCH --time=02:00:00
source ~/.bashrc
mamba activate asap2025e
python3 03_calculate_tanimoto_combo.py \
--ref-ligand-sdf /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_x_series_active_site_cache_20250212/ligand_files_20250212/combined_3d.sdf \
--query-ligand-sdf /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_p_series_curated_cache_20250113/ligand_files_20250113/combined_3d.sdf \
--output-dir /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_p_series_curated_cache_20250113/ligand_files_20250113/tanimoto_combo_p_to_x
