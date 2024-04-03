#BSUB -J "run_self_docking_multiple_poses"
#BSUB -oo %J.out
#BSUB -eo %J.stderr
#BSUB -n 32
#BSUB -q cpuqueue
#BSUB -R rusage[mem=4]
#BSUB -W 2:00

source ~/.bashrc
conda activate asapdiscovery

asap-docking cross-docking \
--target SARS-CoV-2-Mpro \
--use-omega \
--allow-retries \
--structure-selector SelfDockingSelector \
--fragalysis-dir /data/chodera/asap-datasets/mpro_fragalysis-04-01-24 \
--no-save-to-cache \
--cache-dir /data/chodera/asap-datasets/mpro_fragalysis-04-01-24_curated_cache \
--use-only-cache \
--use-dask \
--dask-type lilac-cpu \
--output-dir /lila/data/chodera/asap-datasets/retro_docking/sars_fragalysis_retrospective/20240403_multi_pose_docking_self_docking \
--overwrite

