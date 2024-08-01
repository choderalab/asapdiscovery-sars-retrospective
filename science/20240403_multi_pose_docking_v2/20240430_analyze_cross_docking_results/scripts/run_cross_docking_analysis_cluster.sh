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
# network device info
ulimit -c 0

python3 run_full_cross_docking_evaluation.py \
--input /home/paynea/asap-datasets/retro_docking/sars_fragalysis_retrospective/20240424_multi_pose_docking_cross_docking/results_csvs/20240503_combined_results_with_data.csv \
--output analyzed_data/ \
--date_dict_path /data/chodera/paynea/asapdiscovery-sars-retrospective/science/20240403_multi_pose_docking_v2/20240430_analyze_cross_docking_results/20240503_inputs_analysis/date_dict.json \
--n_cpus 128

date
echo Done
