#python3 03_combine_and_process_results.py \
#-r /Users/alexpayne/Scientific_Projects/mers-drug-discovery/sars2-retrospective-analysis/20241018_fred_docking/rmsd_csvs/ \
#-c /Users/alexpayne/Scientific_Projects/mers-drug-discovery/sars2-retrospective-analysis/mpro_fragalysis-04-01-24_curated_cache_p_series \
#-d /Users/alexpayne/Scientific_Projects/asapdiscovery-sars-retrospective/science/20240403_multi_pose_docking_v2/20240430_analyze_cross_docking_results/20240503_inputs_analysis \
#-o '20241205_combined_results_with_data.csv'
#python3 03_combine_and_process_results.py \
#-r /data/chodera/asap-datasets/retro_docking/sars_fragalysis_retrospective/20241018_fred_docking/rmsd_csvs \
#-c /data/chodera/asap-datasets/mpro_fragalysis-04-01-24_curated_cache_p_series \
#-d /data/chodera/paynea/asapdiscovery-sars-retrospective/science/20240403_multi_pose_docking_v2/20240430_analyze_cross_docking_results/20240503_inputs_analysis \
#-o /data/chodera/asap-datasets/retro_docking/sars_fragalysis_retrospective/20241018_fred_docking/rmsd_csvs/20241205_combined_results_with_data.csv
source ~/.bashrc
conda activate asap2025e
python3 02_combine_and_process_results.py \
-r /data1/choderaj/paynea/asap-datasets/20250212_p_to_x_fred/rmsd_csvs \
-c /data1/choderaj/paynea/asap-datasets/mpro_fragalysis-04-01-24_x_series_active_site_cache_20250212 \
-d /data1/choderaj/paynea/asapdiscovery-sars-retrospective/science/20240403_multi_pose_docking_v2/20240430_analyze_cross_docking_results/20240503_inputs_analysis \
-o /data1/choderaj/paynea/asap-datasets/20250212_p_to_x_fred/rmsd_csvs/20250217_combined_results_with_data.csv