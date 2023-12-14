#BSUB -J run_cross_docking
#BSUB -oo run_cross_docking_%I.out
#BSUB -eo run_cross_docking_%I.stderr
#BSUB -n 1
#BSUB -q cpuqueue
#BSUB -R rusage[mem=256]
#BSUB -W 24:00

source ~/.bashrc
conda activate asapdiscovery

asap-docking cross-docking --input-json cross_docking.inputs.json
 
