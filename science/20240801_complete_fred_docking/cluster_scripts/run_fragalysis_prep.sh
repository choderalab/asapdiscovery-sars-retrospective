#!/bin/bash
## Example usage:
#BSUB -J "fragalysis_prep"
#BSUB -oo logs/fragalysis_prep.out
#BSUB -eo logs/fragalysis_prep.stderr
#BSUB -n 64
#BSUB -q cpuqueue
#BSUB -R rusage[mem=2]
#BSUB -W 2:00

source ~/.bashrc
conda activate asapdiscovery

echo Start
# network device info
ifconfig
# dask info
dask info versions
ulimit -c 0


asap-prep \
--target SARS-CoV-2-Mpro \
--fragalysis-dir /data/chodera/asap-datasets/mpro_fragalysis-04-01-24_p_series \
--cache-dir /data/chodera/asap-datasets/mpro_fragalysis-04-01-24_curated_cache_p_series \
--output-dir fragalysis_prep_out \
--loop-db /lila/home/kaminowb/.openeye/rcsb_spruce.loop_db \
--save-to-cache \
--use-dask \
--dask-type local

echo Done
date