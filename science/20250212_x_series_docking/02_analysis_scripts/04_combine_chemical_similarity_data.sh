#!/bin/bash
#SBATCH --job-name=combine_chemical_similarity_data
#SBATCH --output=logs/combine_chemical_similarity_data.out
#SBATCH --error=logs/combine_chemical_similarity_data.err
#SBATCH --partition=cpu
#SBATCH --cpus-per-task=1
#SBATCH --mem=64GB
#SBATCH --time=02:00:00
source ~/.bashrc
mamba activate asap2025e
python 04_combine_chemical_similarity_data.py \
/data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_p_series_curated_cache_20250113/ligand_files_20250113/tanimoto_combo_p_to_x/tanimoto_combo.csv \
/data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_p_series_curated_cache_20250113/ligand_files_20250113/mcs_tanimoto_p_to_x/mcs_tanimoto.csv \
/data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_p_series_curated_cache_20250113/ligand_files_20250113/ecfp_tanimoto_p_to_x/fingerprint_similarities.csv
