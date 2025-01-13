#!/bin/bash

# fix misc errors
python3 /data1/choderaj/paynea/asapdiscovery-sars-retrospective/production/covid_moonshot_fragalysis_processing/prep_cache_for_docking.py \
--input_cache /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_p_series_cache_20250110

# save 3d
python3 /data1/choderaj/paynea/asapdiscovery-sars-retrospective/production/covid_moonshot_fragalysis_processing/combined_sdf_from_cache.py \
--input_cache /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_p_series_cache_20250110 \
--output_dir /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_p_series_cache_20250110/combined_split_3d_20250113/

# save 2d
python3 /data1/choderaj/paynea/asapdiscovery-sars-retrospective/production/covid_moonshot_fragalysis_processing/combined_sdf_from_cache.py \
--input_cache /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_p_series_cache_20250110 \
--output_dir /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_p_series_cache_20250110/combined_split_3d_20250113/ \
--flatten

python3 /data1/choderaj/paynea/asapdiscovery-sars-retrospective/production/utils/split_sdf.py \
--sdf_fn /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_p_series_cache_20250110/combined_split_3d_20250113/combined_3d.sdf \
--out_dir /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_p_series_cache_20250110/combined_split_3d_20250113/ \
--chunk_size 1 \
--name_convention "integer"