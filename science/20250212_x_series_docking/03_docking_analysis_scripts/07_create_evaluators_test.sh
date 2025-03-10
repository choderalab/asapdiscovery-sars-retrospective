#!/bin/zsh

python3 create_evaluators.py \
--input /Users/alexpayne/Scientific_Projects/mers-drug-discovery/sars2-retrospective-analysis/test.csv \
--output test_evaluator_creation \
--update-n-per-split

python3 create_evaluators.py \
--input /Users/alexpayne/Scientific_Projects/mers-drug-discovery/sars2-retrospective-analysis/test.csv \
--output test_evaluator_creation_similarity_split \
--update-n-per-split \
--settings 'settings_similarity_split.yml'
