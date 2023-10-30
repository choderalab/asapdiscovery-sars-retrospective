#!/bin/bash
## Example usage:
## bsub -J "run_self_docking[1-219]" < run_self_docking_hybrid_array.sh

#BSUB -oo run_self_hybrid_2d_%I.out
#BSUB -eo run_self_hybrid_2d_%I.stderr
#BSUB -n 1
#BSUB -q cpuqueue
#BSUB -R rusage[mem=4]
#BSUB -W 0:10

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
conda activate ad-3.9
run-docking-oe \
-l "/lila/data/chodera/asap-datasets/current/sars_01_prepped_v3/sdf_lsf_array_p_only_by_name_2d/"$cmpd".sdf" \
-r '/lila/data/chodera/asap-datasets/current/sars_01_prepped_v3/*'$cmpd'*/*_prepped_receptor_0.oedu' \
-o /lila/data/chodera/asap-datasets/retro_docking/sars_fragalysis_retrospective/20231016_self_docked_hybrid_p_only_2d \
-n 1 \
--docking_sys posit \
--omega \
--relax clash \
--timeout 600 \
--max_failures 300 \
--posit_method hybrid \
-log "run_docking_oe."$LSB_JOBINDEX
echo Done
date
