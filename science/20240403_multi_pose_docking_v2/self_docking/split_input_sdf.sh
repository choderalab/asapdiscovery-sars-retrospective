#!/bin/bash

python ../../production/utils/split_sdf.py \
-i /data/chodera/asap-datasets/mpro_fragalysis-04-01-24_curated_cache/combined.sdf \
-o /data/chodera/asap-datasets/mpro_fragalysis-04-01-24_curated_cache/combined_split_2d \
-n 1 \
--name_convention "integer" \
--flatten