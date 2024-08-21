#!/bin/bash
## Example usage:
## bsub -J "multiple_poses[1-205]" < run_cross_docking_multiple_poses_local_dask_multipose_saving_array.sh

#BSUB -oo logs/multiple_poses_%I.out
#BSUB -eo logs/multiple_poses_%I.stderr
#BSUB -n 8
#BSUB -m lt-gpu
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


python test_import_speed.py

echo Done
date