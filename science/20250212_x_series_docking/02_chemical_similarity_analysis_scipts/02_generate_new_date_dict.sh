#!/bin/bash
#SBATCH --job-name=generate_date_dict
#SBATCH --output=logs/generate_date_dict_%A_%a.out
#SBATCH --error=logs/generate_date_dict_%A_%a.err
#SBATCH --cpus-per-task 1
#SBATCH --partition=cpu
#SBATCH --mem=64GB
#SBATCH --time=00:30:00

source ~/.bashrc
conda activate asap2025e
python3 /data1/choderaj/paynea/asapdiscovery-sars-retrospective/production/covid_moonshot_fragalysis_processing/generate_date_dict.py \
--fragalysis-dir /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_x_series_active_site \
--output-dir /data1/choderaj/paynea/asapdiscovery-sars-retrospective/data/cmpd_date_dict