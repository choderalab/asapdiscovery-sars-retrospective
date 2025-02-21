#!/bin/bash
#SBATCH --job-name=combine_and_process
#SBATCH --output=logs/combine_and_process_%A_%a.out
#SBATCH --error=logs/combine_and_process_%A_%a.err
#SBATCH --cpus-per-task 1
#SBATCH --partition=cpu
#SBATCH --mem=64GB
#SBATCH --time=00:30:00

source ~/.bashrc
conda activate asap2025e
python3 05_combine_and_process_results.py \
-r /data1/choderaj/paynea/asap-datasets/20250212_p_to_x_posit/rmsd_csvs \
--protein-cache /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_x_series_active_site_cache_20250212 \
--ligand-cache /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_p_series_curated_cache_20250113 \
--data-path /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_p_series_curated_cache_20250113/ligand_files_20250113/combined_p_to_x_similarities \
--date-dict /data1/choderaj/paynea/asapdiscovery-sars-retrospective/data/cmpd_date_dict/date_dict.json \
-o /data1/choderaj/paynea/asap-datasets/20250212_p_to_x_posit/rmsd_csvs/20250217_combined_results_with_data.csv \
--no-add-padding