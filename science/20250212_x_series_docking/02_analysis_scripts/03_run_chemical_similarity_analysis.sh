#!/bin/bash
#SBATCH --job-name=calculate_chemical_similarity
#SBATCH --output=logs/calculate_chemical_similarity.out
#SBATCH --error=logs/calculate_chemical_similarity.err
#SBATCH --cpus-per-task 32
#SBATCH --partition=cpu
#SBATCH --mem=64GB
#SBATCH --time=00:30:00
source ~/.bashrc
mamba activate asap2025e
python3 03_run_chemical_similarity_analysis.py \
--ref-ligand-sdf /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_p_series_curated_cache_20250113/ligand_files_20250113/combined_3d.sdf \
--output-dir /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_p_series_curated_cache_20250113/ligand_files_20250113/cpu32 \
--resume \
--n-processes 32
