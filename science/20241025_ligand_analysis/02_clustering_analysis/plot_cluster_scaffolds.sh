#!/bin/zsh
cluster_label_csvs=(../data/bajorath_cluster_labels.csv ../data/default_cluster_labels.csv ../data/csk_cluster_labels.csv ../data/generic_cluster_labels.csv ../data/LFMVB-0SGC8_2024-11-14_20_43_21_616678_sarkush_output.csv)
for cluster_label_csv in $cluster_label_csvs
do
    python3 plot_cluster_scaffolds.py \
    --input_csv $cluster_label_csv \
    --output_dir ../figures \
    --compound_data ../data/unique_compounds.csv

    python3 plot_clusters_over_time.py \
    --input_csv $cluster_label_csv \
    --output_dir ../figures \
    --compound_data ../data/unique_compounds.csv
done
