#!/usr/bin/env bash


#SBATCH --job-name=plot_clean_lcs 
#SBATCH --output=%x.o%j
#SBATCH --error=%x.e%j 
#SBATCH --partition=nocona 
#SBATCH --nodes 1
#SBATCH --cpus-per-task 2 
#SBATCH --ntasks=16

for i in 1 2 3 4; do
    for j in 1 2 3 4; do
	cd "cam$i""-ccd$j"
	pwd
	srun --ntasks=1 --cpus-per-task=${SLURM_CPUS_PER_TASK} --account=${ACCOUNT} ${PIPELINE_DIR}/plotting/plot_TNS_cleaned_lc.py  "$1"/lc_*cleaned  --bkg --mag &
	cd ..
    done
done

wait
echo "done!?"
