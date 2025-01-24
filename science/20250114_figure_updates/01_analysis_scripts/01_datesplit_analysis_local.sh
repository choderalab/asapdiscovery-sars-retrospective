#!/bin/zsh
python 01_datesplit_analysis.py \
--input /Users/alexpayne/Scientific_Projects/mers-drug-discovery/sars2-retrospective-analysis/20240424_multi_pose_docking_cross_docking/results_csvs/20240503_combined_results_with_data.csv \
--output analyzed_data/ \
--date_dict_path /Users/alexpayne/Scientific_Projects/asapdiscovery-sars-retrospective/science/20240403_multi_pose_docking_v2/20240430_analyze_cross_docking_results/20240503_inputs_analysis/date_dict.json \
--n_cpus 4