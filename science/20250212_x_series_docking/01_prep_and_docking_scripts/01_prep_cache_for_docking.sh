#!/bin/bash
source ~/.bashrc
mamba activate asap2025

cache=/data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_x_series_active_site_cache_20250212
ligand_files=$cache/ligand_files_20250212

# fix misc errors
python3 /data1/choderaj/paynea/asapdiscovery-sars-retrospective/production/covid_moonshot_fragalysis_processing/prep_cache_for_docking.py \
--input_cache $cache \

# save 3d
python3 /data1/choderaj/paynea/asapdiscovery-sars-retrospective/production/covid_moonshot_fragalysis_processing/combined_sdf_from_cache.py \
--input_cache $cache \
--output_dir $ligand_files

# save 2d
python3 /data1/choderaj/paynea/asapdiscovery-sars-retrospective/production/covid_moonshot_fragalysis_processing/combined_sdf_from_cache.py \
--input_cache $cache \
--output_dir $ligand_files \
--flatten

# split 3d
python3 /data1/choderaj/paynea/asapdiscovery-sars-retrospective/production/utils/split_sdf.py \
--sdf_fn $ligand_files/combined_3d.sdf \
--out_dir $ligand_files/split_3d/ \
--chunk_size 1 \
--name_convention "integer"

# split 2d
python3 /data1/choderaj/paynea/asapdiscovery-sars-retrospective/production/utils/split_sdf.py \
--sdf_fn $ligand_files/combined_2d.sdf \
--out_dir $ligand_files/split_2d \
--chunk_size 1 \
--name_convention "integer"