#!/bin/bash
## Example usage:
## bsub < run_cross_docking_multiple_poses_local_dask.sh

#BSUB -J "run_cross_docking_multiple_poses_local_dask"
#BSUB -oo logs/multiple_poses.out
#BSUB -eo logs/multiple_poses.stderr
#BSUB -n 32
#BSUB -m lt-gpu
#BSUB -q cpuqueue
#BSUB -R rusage[mem=4]
#BSUB -W 4:00

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
--allow-retries \
--structure-selector LeaveSimilarOutSelector \
--fragalysis-dir /data/chodera/asap-datasets/mpro_fragalysis-04-01-24 \
--ligands "/data/chodera/asap-datasets/mpro_fragalysis-04-01-24_curated_cache/combined_2d.sdf" \
--no-save-to-cache \
--cache-dir /data/chodera/asap-datasets/mpro_fragalysis-04-01-24_curated_cache \
--use-only-cache \
--output-dir "/lila/data/chodera/asap-datasets/retro_docking/sars_fragalysis_retrospective/20240424_multi_pose_docking_cross_docking" \
--no-overwrite \
--num-poses 50 \
--use-dask \
--dask-type local \
--loglevel DEBUG

echo Done
date
