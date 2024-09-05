#!/bin/bash

python3 /data/chodera/paynea/asapdiscovery-sars-retrospective/production/covid_moonshot_fragalysis_processing/combined_sdf_from_cache.py \
--input_cache /data/chodera/asap-datasets/mpro_fragalysis-04-01-24_curated_cache/ \
--output_dir /data/chodera/asap-datasets/mpro_fragalysis-04-01-24_curated_cache/combined_split_3d_20240903/

python3 /data/chodera/paynea/asapdiscovery-sars-retrospective/production/utils/split_sdf.py \
--sdf_fn /data/chodera/asap-datasets/mpro_fragalysis-04-01-24_curated_cache/combined_split_3d_20240903/combined_3d.sdf \
--output_dir /data/chodera/asap-datasets/mpro_fragalysis-04-01-24_curated_cache/combined_split_3d_20240903/ \
--chunk_size 1 \
--name_convention "integer"