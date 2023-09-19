#!/bin/bash
## Example usage:
## bsub -J "run_self_docking[0-218]" < run_self_docking_shapefit_array.sh

#BSUB -oo run_self_docking_%I.out
#BSUB -eo run_self_docking_%I.stderr
#BSUB -n 16
#BSUB -q cpuqueue
#BSUB -R rusage[mem=4]
#BSUB -W 2:00

## load file name from array
declare -a cmpd_arr
cmpds=$(ls /lila/data/chodera/asap-datasets/current/sars_01_prepped_v3/sdf_lsf_array_p_only_by_name/*.sdf | sed -e 's/\/.*\///g' | sed -e 's/\.sdf$//')
i=0
for cmpd in $cmpds; do
cmpd_arr[ $i ]=$cmpd
(( i++ ))
done

cmpd=${cmpd_arr[ $LSB_JOBINDEX-1]}
echo $cmpd

source ~/.bashrc
conda activate ad-3.9
run-docking-oe \
-l "/lila/data/chodera/asap-datasets/current/sars_01_prepped_v3/sdf_lsf_array_p_only_by_name/"$cmpd".sdf" \
-r '/lila/data/chodera/asap-datasets/current/sars_01_prepped_v3/*'$cmpd'*/*_prepped_receptor_0.oedu' \
-o /lila/data/chodera/asap-datasets/retro_docking/sars_fragalysis_retrospective/20230919_self_docked_shapefit_p_only \
-n 16 \
--omega \
--relax clash \
--timeout 600 \
--max_failures 300 \
--shapefit \
-log "run_docking_oe."$LSB_JOBINDEX
echo Done
date
