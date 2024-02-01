#!/bin/bash
## Example usage:
## bsub -J "run_cross_docking[1-219]" < run_cross_docking_array.sh

#BSUB -oo logs/run_cross_docking_%I.out
#BSUB -eo logs/run_cross_docking_%I.stderr
#BSUB -n 1
#BSUB -q cpuqueue
#BSUB -R rusage[mem=128]
#BSUB -W 2:00

## load file name from array
declare -a cmpd_arr
cmpds=$(ls /lila/data/chodera/asap-datasets/current/sars_01_prepped_v3/sdf_lsf_array_p_only_by_name_2d/*.sdf | sed -e 's/\/.*\///g' | sed -e 's/\.sdf$//')
i=0
for cmpd in $cmpds; do
cmpd_arr[ $i ]=$cmpd
(( i++ ))
done

cmpd=${cmpd_arr[ $LSB_JOBINDEX-1]}
echo $cmpd

source ~/.bashrc
conda activate asapdiscovery

asap-docking cross-docking \
--overwrite \
--target SARS-CoV-2-Mpro \
--structure-selector LeaveSimilarOutSelector \
--use-omega --allow-retries --allow-final-clash --multi-reference \
--ligands "/lila/data/chodera/asap-datasets/current/sars_01_prepped_v3/sdf_lsf_array_p_only_by_name_2d/"$cmpd".sdf" \
--structure-dir /lila/data/chodera/asap-datasets/current/sars_01_prepped_v3/pdb_cache_p_only \
--cache-dir /lila/data/chodera/asap-datasets/current/sars_01_prepped_v3/du_cache_p_only \
--output-dir "/lila/data/chodera/asap-datasets/retro_docking/sars_fragalysis_retrospective/20240110_cross_docking_p_only_2d_multi_reference/"$cmpd \
--use-only-cache 
