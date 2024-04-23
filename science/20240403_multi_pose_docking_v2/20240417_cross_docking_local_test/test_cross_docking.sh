#!/bin/zsh
i=$1
asap-docking cross-docking \
--target SARS-CoV-2-Mpro \
--use-omega \
--allow-retries \
--structure-selector LeaveSimilarOutSelector \
--pdb-file /Users/alexpayne/Scientific_Projects/mers-drug-discovery/sars2-retrospective-analysis/mpro_fragalysis-04-01-24/aligned/Mpro-P2201_0A/Mpro-P2201_0A_bound.pdb \
--ligands "/Users/alexpayne/Scientific_Projects/mers-drug-discovery/sars2-retrospective-analysis/mpro_fragalysis-04-01-24_curated_cache/combined_split_2d/$i.sdf" \
--no-save-to-cache \
--cache-dir /Users/alexpayne/Scientific_Projects/mers-drug-discovery/sars2-retrospective-analysis/mpro_fragalysis-04-01-24_curated_cache \
--use-only-cache \
--output-dir "/Users/alexpayne/Scientific_Projects/mers-drug-discovery/sars2-retrospective-analysis/20240403_multi_pose_docking_cross_docking/$i.sdf" \
--overwrite \
--num-poses 50

#--fragalysis-dir /Users/alexpayne/Scientific_Projects/mers-drug-discovery/sars2-retrospective-analysis/mpro_fragalysis-04-01-24 \