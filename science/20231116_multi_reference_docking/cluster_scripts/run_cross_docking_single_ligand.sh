#BSUB -J run_cross_docking
#BSUB -oo run_cross_docking_%I.out
#BSUB -eo run_cross_docking_%I.stderr
#BSUB -n 1
#BSUB -q cpuqueue
#BSUB -R rusage[mem=8]
#BSUB -W 2:00

source ~/.bashrc
conda activate asapdiscovery

asap-docking cross-docking \
--target SARS-CoV-2-Mpro \
--use-omega --allow-retries --allow-final-clash --multi-reference \
--structure-selector LeaveOneOutSelector \
--ligands /lila/data/chodera/asap-datasets/current/sars_01_prepped_v3/sdf_lsf_array_p_only_by_name_2d/MAT-POS-5cd9ea36-22.sdf \
--structure-dir /lila/data/chodera/asap-datasets/current/sars_01_prepped_v3/pdb_cache_small \
--cache-dir /lila/data/chodera/asap-datasets/current/sars_01_prepped_v3/du_cache_p_only \
--cache-type DesignUnit \
--use-dask \
--dask-type lilac-cpu \
--output-dir /lila/data/chodera/asap-datasets/retro_docking/sars_fragalysis_retrospective/20231116_cross_docking_test_multi_reference
 
