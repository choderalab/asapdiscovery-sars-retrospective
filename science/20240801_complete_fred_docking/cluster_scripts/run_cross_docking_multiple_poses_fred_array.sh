#!/bin/bash
## Example usage:
## bsub -J "fred_multiple_poses[1-205]" < run_cross_docking_multiple_poses_fred_array.sh

#BSUB -oo logs/fred_%I.out
#BSUB -eo logs/fred_%I.stderr
#BSUB -n 8
#BSUB -q cpuqueue
#BSUB -R rusage[mem=12]
#BSUB -W 24:00

source ~/.bashrc
conda activate asapdiscovery

echo Start
# network device info
ifconfig
# dask info
dask info versions
ulimit -c 0


asap-docking cross-docking \
--target SARS-CoV-2-Mpro \
--use-omega \
--omega-dense \
--allow-retries \
--allow-final-clash \
--posit-method FRED \
--structure-selector PairwiseSelector \
--fragalysis-dir /data/chodera/asap-datasets/mpro_fragalysis-04-01-24_p_series \
--ligands "/data/chodera/asap-datasets/mpro_fragalysis-04-01-24_curated_cache/combined_split_2d/$LSB_JOBINDEX.sdf" \
--cache-dir /data/chodera/asap-datasets/mpro_fragalysis-04-01-24_curated_cache_p_series \
--output-dir "/lila/data/chodera/asap-datasets/retro_docking/sars_fragalysis_retrospective/20241018_fred_docking/$LSB_JOBINDEX" \
--no-overwrite \
--no-save-to-cache \
--use-only-cache \
--num-poses 50 \
--use-dask \
--dask-type local

echo Done
date
