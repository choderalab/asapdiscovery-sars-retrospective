#!/bin/zsh

echo Start

asap-cli protein-prep \
--target SARS-CoV-2-Mpro \
--fragalysis-dir /Users/alexpayne/Scientific_Projects/mers-drug-discovery/sars2-retrospective-analysis/mpro_fragalysis-04-01-24_p_series_test \
--cache-dir /Users/alexpayne/Scientific_Projects/mers-drug-discovery/sars2-retrospective-analysis/mpro_fragalysis-04-01-24_curated_cache_p_series_test_v2 \
--output-dir fragalysis_prep_out \
--save-to-cache \
--ref-chain A \
--active-site-chain A \
#--use-dask \
#--dask-type local

echo Done
date

#--loop-db /lila/home/kaminowb/.openeye/rcsb_spruce.loop_db \