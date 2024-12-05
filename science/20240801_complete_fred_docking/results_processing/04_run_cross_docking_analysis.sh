#!/bin/bash
## Example usage:

#BSUB -J cross_docking_analysis
#BSUB -oo logs/cross_docking_analysis.out
#BSUB -eo logs/cross_docking_analysis.stderr
#BSUB -n 64
#BSUB -m lt-gpu
#BSUB -q cpuqueue
#BSUB -R rusage[mem=1]
#BSUB -W 2:00

source ~/.bashrc
mamba activate harbor

echo Start
date
# network device info
ulimit -c 0

python3 04_run_cross_docking_analysis.py \
--input /data/chodera/asap-datasets/retro_docking/sars_fragalysis_retrospective/20241018_fred_docking/rmsd_csvs/20241205_combined_results_with_data.csv \
--output /data/chodera/paynea/asapdiscovery-sars-retrospective/science/20240801_complete_fred_docking/analyzed_data \
--n_cpus 64

date
echo Done
