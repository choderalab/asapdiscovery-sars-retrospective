#!/bin/zsh

#python3 run_evaluators.py \
#--input /Users/alexpayne/Scientific_Projects/mers-drug-discovery/sars2-retrospective-analysis/test.csv \
#--output test_run_evaluators \
#--n-cpus 1 \
#--job-id 'my_only_job' \
#--evaluator-json test_evaluator_creation/evaluator_*.json

python3 08_run_evaluators.py \
--input /Users/alexpayne/Scientific_Projects/mers-drug-discovery/sars2-retrospective-analysis/test.csv \
--output test_run_evaluators \
--n-cpus 1 \
--job-id 'similarity_split' \
--evaluator-json test_evaluator_creation_similarity_split/evaluator_*.json