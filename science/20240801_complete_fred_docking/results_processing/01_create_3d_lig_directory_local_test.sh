#!/bin/zsh

python3 /Users/alexpayne/Scientific_Projects/asapdiscovery-sars-retrospective/production/covid_moonshot_fragalysis_processing/combined_sdf_from_cache.py \
--input_cache /Users/alexpayne/Scientific_Projects/mers-drug-discovery/sars2-retrospective-analysis/mpro_fragalysis-04-01-24_curated_cache_p_series \
--output_dir /Users/alexpayne/Scientific_Projects/mers-drug-discovery/sars2-retrospective-analysis/mpro_fragalysis-04-01-24_curated_cache_p_series/combined_split_3d_20250107/
#/Users/alexpayne/Scientific_Projects/mers-drug-discovery/sars2-retrospective-analysis/mpro_fragalysis-04-01-24_p_series_test
#/Users/alexpayne/Scientific_Projects/mers-drug-discovery/sars2-retrospective-analysis/mpro_fragalysis-04-01-24_curated_cache_p_series_test
#python3 /Users/alexpayne/Scientific_Projects/asapdiscovery-sars-retrospective/production/utils/split_sdf.py \
#--sdf_fn /Users/alexpayne/Scientific_Projects/mers-drug-discovery/sars2-retrospective-analysis/mpro_fragalysis-04-01-24_curated_cache_p_series/combined_split_3d_20250107 \
#--out_dir /data/chodera/asap-datasets/mpro_fragalysis-04-01-24_curated_cache/combined_split_3d_20240903/ \
#--chunk_size 1 \
#--name_convention "integer"