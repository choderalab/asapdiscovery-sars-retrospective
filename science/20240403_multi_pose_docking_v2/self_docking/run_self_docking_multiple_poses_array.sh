#!/bin/bash
## Example usage:
## bsub -J "run_self_docking_multiple_poses[1-205]" < run_self_docking_multiple_poses_array.sh

#BSUB -oo array_logs/run_self_docking_multiple_poses_%I.out
#BSUB -eo array_logs/run_self_docking_multiple_poses_%I.out
#BSUB -n 1
#BSUB -q cpuqueue
#BSUB -R rusage[mem=4]
#BSUB -W 0:10

source ~/.bashrc
conda activate asapdiscovery

asap-docking cross-docking \
--target SARS-CoV-2-Mpro \
--use-omega \
--allow-retries \
--structure-selector SelfDockingSelector \
--fragalysis-dir /data/chodera/asap-datasets/mpro_fragalysis-04-01-24 \
--ligands "/data/chodera/asap-datasets/mpro_fragalysis-04-01-24_curated_cache/combined_split_2d/$LSB_JOBIDEX.sdf" \
--no-save-to-cache \
--cache-dir /data/chodera/asap-datasets/mpro_fragalysis-04-01-24_curated_cache \
--use-only-cache \
--output-dir /lila/data/chodera/asap-datasets/retro_docking/sars_fragalysis_retrospective/20240403_multi_pose_docking_self_docking \
--overwrite \
--num-poses 50
