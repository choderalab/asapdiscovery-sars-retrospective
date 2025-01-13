#!/bin/bash
source ~/.bashrc
mamba activate asap2025

# fix misc errors
python3 /data1/choderaj/paynea/asapdiscovery-sars-retrospective/production/covid_moonshot_fragalysis_processing/prep_cache_for_docking.py \
--input_cache /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_p_series_curated_cache_20250113

# save 3d
python3 /data1/choderaj/paynea/asapdiscovery-sars-retrospective/production/covid_moonshot_fragalysis_processing/combined_sdf_from_cache.py \
--input_cache /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_p_series_curated_cache_20250113 \
--output_dir /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_p_series_curated_cache_20250113/ligand_files_20250113/

# save 2d
python3 /data1/choderaj/paynea/asapdiscovery-sars-retrospective/production/covid_moonshot_fragalysis_processing/combined_sdf_from_cache.py \
--input_cache /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_p_series_curated_cache_20250113 \
--output_dir /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_p_series_curated_cache_20250113/ligand_files_20250113/ \
--flatten

# split 3d
python3 /data1/choderaj/paynea/asapdiscovery-sars-retrospective/production/utils/split_sdf.py \
--sdf_fn /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_p_series_curated_cache_20250113/ligand_files_20250113/combined_3d.sdf \
--out_dir /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_p_series_curated_cache_20250113/ligand_files_20250113/split_3d/ \
--chunk_size 1 \
--name_convention "integer"

# split 2d
python3 /data1/choderaj/paynea/asapdiscovery-sars-retrospective/production/utils/split_sdf.py \
--sdf_fn /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_p_series_curated_cache_20250113/ligand_files_20250113/combined_2d.sdf \
--out_dir /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_p_series_curated_cache_20250113/ligand_files_20250113/split_2d \
--chunk_size 1 \
--name_convention "integer"