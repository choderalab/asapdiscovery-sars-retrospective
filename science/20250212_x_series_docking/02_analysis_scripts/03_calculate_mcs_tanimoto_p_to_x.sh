#!/bin/bash
#SBATCH --job-name=calculate_mcs_tanimoto
#SBATCH --output=logs/calculate_mcs_tanimoto.out
#SBATCH --error=logs/calculate_mcs_tanimoto.err
#SBATCH --partition=cpu
#SBATCH --cpus-per-task=32
#SBATCH --mem=64GB
#SBATCH --time=02:00:00
#SBATCH --array=1-218  # Array jobs range (for jobs 1 through n)
source ~/.bashrc
mamba activate asap2025e
python3 03_calculate_mcs_tanimoto.py \
--ref-ligand-sdf /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_x_series_active_site_cache_20250212/ligand_files_20250212/combined_3d.sdf \
--query-ligand-sdf "/data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_p_series_curated_cache_20250113/ligand_files_20250113/split_2d/${SLURM_ARRAY_TASK_ID}.sdf" \
--output-dir /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_p_series_curated_cache_20250113/ligand_files_20250113/mcs_tanimoto_p_to_x
