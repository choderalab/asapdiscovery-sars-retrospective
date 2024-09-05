#!/bin/bash
## Example usage:
## bsub -J "calculate_rmsd[1-205]" < calculate_rmsd_array.sh

#BSUB -oo logs/calculate_rmsd_array_%I.out
#BSUB -eo logs/calculate_rmsd_array_%I.stderr
#BSUB -n 1
#BSUB -m lt-gpu
#BSUB -q cpuqueue
#BSUB -R rusage[mem=12]
#BSUB -W 0:05

source ~/.bashrc
conda activate asapdiscovery

echo Start
# network device info
ifconfig
# dask info
dask info versions
ulimit -c 0

python3.10 02_calculate_rmsd_from_docking_results.py \
-d "/lila/data/chodera/asap-datasets/retro_docking/sars_fragalysis_retrospective/20240816_fred_docking/$LSB_JOBINDEX" \
-l "/data/chodera/asap-datasets/mpro_fragalysis-04-01-24_curated_cache/combined_split_3d_20240903/"$LSB_JOBINDEX".sdf" \
-o "/lila/data/chodera/asap-datasets/retro_docking/sars_fragalysis_retrospective/20240816_fred_docking/rmsd_csvs/$LSB_JOBINDEX.csv"

echo Done
date
