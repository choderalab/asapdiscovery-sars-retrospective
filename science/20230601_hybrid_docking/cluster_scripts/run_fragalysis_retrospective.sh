#!/bin/bash
#BSUB -J run_oe_docking
#BSUB -oo run_fragalysis_retrospective.out
#BSUB -eo run_fragalysis_retrospective.stderr
#BSUB -n 32
#BSUB -q cpuqueue
#BSUB -R rusage[mem=4]
#BSUB -W 24:00
source ~/.bashrc
conda activate ad-3.9
run-docking-oe \
-l /lila/data/chodera/asap-datasets/current/sars_01_prepped_v3/Mpro_combined_labeled_p_only.sdf \
-r '/lila/data/chodera/asap-datasets/current/sars_01_prepped_v3/Mpro-P*/*_prepped_receptor_0.oedu' \
-o /lila/data/chodera/asap-datasets/retro_docking/sars_fragalysis_retrospective/20230606_hybrid_p_only \
-n 32 \
--omega \
--relax clash \
--hybrid
echo Done
date
