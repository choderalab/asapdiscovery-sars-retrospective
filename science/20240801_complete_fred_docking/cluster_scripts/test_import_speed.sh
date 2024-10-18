#!/bin/bash
## Example usage:
#BSUB -J test_import_speed
#BSUB -oo logs/test_import_speed.out
#BSUB -eo logs/test_import_speed.stderr
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


python3 test_import_speed.py

echo Done
date
