#BSUB -J "run_self_docking_multiple_poses"
#BSUB -oo run_self_docking_multiple_poses.out
#BSUB -eo run_self_docking_multiple_poses.stderr
#BSUB -n 32
#BSUB -q gpuqueue
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
--ligands /data/chodera/asap-datasets/mpro_fragalysis-04-01-24_curated_cache/combined.sdf \
--no-save-to-cache \
--cache-dir /data/chodera/asap-datasets/mpro_fragalysis-04-01-24_curated_cache \
--use-only-cache \
--output-dir /lila/data/chodera/asap-datasets/retro_docking/sars_fragalysis_retrospective/20240403_multi_pose_docking_self_docking \
--overwrite \
--num-poses 50
