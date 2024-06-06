#!/bin/bash
## Example usage:
## bsub -J deduplicate_docked_poses[1-205] < 20240606_deduplicate_docked_poses_array.sh
#BSUB -oo logs/deduplicate_docked_poses_%I.out
#BSUB -eo logs/deduplicate_docked_poses_%I.stderr
#BSUB -n 64
#BSUB -m lt-gpu
#BSUB -q cpuqueue
#BSUB -R rusage[mem=1]
#BSUB -W 2:00

source ~/.bashrc
mamba activate asapdiscovery

echo Start
date
# network device info
ulimit -c 0

python3 filter_similar_molecules.py \
--dock-dir "/home/paynea/asap-datasets/retro_docking/sars_fragalysis_retrospective/20240424_multi_pose_docking_cross_docking"$LSB_JOBINDEX \
--out-dir "/home/paynea/asap-datasets/retro_docking/sars_fragalysis_retrospective/20240424_multi_pose_docking_cross_docking/20240606_deduplicated_docked_poses/"$LSB_JOBINDEX

date
echo Done