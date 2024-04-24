#!/bin/bash
## Example usage:
## bsub < run_cross_docking_multiple_poses_local_dask.sh

#BSUB -J "run_cross_docking_multiple_poses_local_dask"
#BSUB -oo logs/multiple_poses_test.out
#BSUB -eo logs/multiple_poses_test.stderr
#BSUB -n 8
#BSUB -m lt-gpu
#BSUB -R "span[hosts=1]"
#BSUB -R rusage[mem=16]
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
--allow-retries \
--structure-selector LeaveSimilarOutSelector \
--pdb-file /data/chodera/asap-datasets/mpro_fragalysis-04-01-24/aligned/Mpro-P2201_0A/Mpro-P2201_0A_bound.pdb \
--ligands "/data/chodera/asap-datasets/mpro_fragalysis-04-01-24_curated_cache/combined_2d.sdf" \
--no-save-to-cache \
--cache-dir /data/chodera/asap-datasets/mpro_fragalysis-04-01-24_curated_cache \
--use-only-cache \
--output-dir "/lila/data/chodera/asap-datasets/retro_docking/sars_fragalysis_retrospective/20240424_multi_pose_docking_cross_docking" \
--overwrite \
--num-poses 50 \
--use-dask \
--dask-type local \
--loglevel DEBUG

echo Done
date
