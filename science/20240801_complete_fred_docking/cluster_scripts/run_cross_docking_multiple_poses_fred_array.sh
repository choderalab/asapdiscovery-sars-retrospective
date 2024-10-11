#!/bin/bash
## Example usage:
## bsub -J "fred_multiple_poses[1-205]" < run_cross_docking_multiple_poses_fred_array.sh

#BSUB -oo logs/fred_%I.out
#BSUB -eo logs/fred_%I.stderr
#BSUB -n 8
#BSUB -q cpuqueue
#BSUB -R rusage[mem=12]
#BSUB -W 2:00

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
--fragalysis-dir /data/chodera/asap-datasets/mpro_fragalysis-04-01-24 \
--ligands "/data/chodera/asap-datasets/mpro_fragalysis-04-01-24_curated_cache/combined_split_2d/$LSB_JOBINDEX.sdf" \
--no-save-to-cache \
--cache-dir /data/chodera/asap-datasets/mpro_fragalysis-04-01-24_curated_cache \
--use-only-cache \
--output-dir "/lila/data/chodera/asap-datasets/retro_docking/sars_fragalysis_retrospective/20240925_fred_docking/$LSB_JOBINDEX" \
--no-overwrite \
--num-poses 50 \
--use-dask \
--dask-type local

echo Done
date
