#!/bin/bash

combine-sdf \
-i "/data/chodera/asap-datasets/mpro_fragalysis-04-01-24_curated_cache" \
-o "/data/chodera/asap-datasets/mpro_fragalysis-04-01-24_curated_cache/"

combine-sdf \
-i "/data/chodera/asap-datasets/mpro_fragalysis-04-01-24_curated_cache" \
-o "/data/chodera/asap-datasets/mpro_fragalysis-04-01-24_curated_cache/" \
--flatten
