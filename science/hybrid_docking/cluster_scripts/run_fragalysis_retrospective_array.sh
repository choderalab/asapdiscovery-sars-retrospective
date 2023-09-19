#!/bin/bash
## Example usage:
## bsub -J "run_fragalysis_retrospective[1-576]" < run_fragalysis_retrospective_array.sh

#BSUB -oo run_fragalysis_retrospective_%I.out
#BSUB -eo run_fragalysis_retrospective_%I.stderr
#BSUB -n 16
#BSUB -q cpuqueue
#BSUB -R rusage[mem=4]
#BSUB -W 2:00
source ~/.bashrc
conda activate ad-3.9
run-docking-oe \
-l "/lila/data/chodera/asap-datasets/current/sars_01_prepped_v3/sdf_lsf_array_p_only/"$LSB_JOBINDEX".sdf" \
-r '/lila/data/chodera/asap-datasets/current/sars_01_prepped_v3/Mpro-P*/*_prepped_receptor_0.oedu' \
-o /lila/data/chodera/asap-datasets/retro_docking/sars_fragalysis_retrospective/20230608_hybrid_p_only \
-n 32 \
--omega \
--relax clash \
--timeout 600 \
--max_failures 300 \
--hybrid \
-log "run_docking_oe."$LSB_JOBINDEX
echo Done
date
