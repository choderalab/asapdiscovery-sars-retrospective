#!/bin/bash
## Example usage:
## bsub -J "run_cross_docking[1-219]" < run_cross_docking_hybrid_array.sh

#BSUB -oo run_cross_hybrid_2d_%I.out
#BSUB -eo run_cross_hybrid_2d_%I.stderr
#BSUB -n 16
#BSUB -q cpuqueue
#BSUB -R rusage[mem=4]
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
run-docking-oe \
-l "/lila/data/chodera/asap-datasets/current/sars_01_prepped_v3/sdf_lsf_array_p_only_by_name_2d/"$cmpd".sdf" \
-r '/lila/data/chodera/asap-datasets/current/sars_01_prepped_v3/Mpro-P*/*_prepped_receptor_0.oedu' \
-o /lila/data/chodera/asap-datasets/retro_docking/sars_fragalysis_retrospective/20231107_cross_docking_p_only_2d_multi_reference \
-n 16 \
--docking_sys posit \
--omega \
--relax clash \
--timeout -1 \
--max_failures 100000 \
--posit_method all \
--num_poses 1 \
-log "run_docking_oe."$LSB_JOBINDEX
echo Done
date
