#!/usr/bin/env bash

####issue one, need to fill in these variables
### fix by removing environment variables....
#SBATCH --job-name="parallel_smooth"
#SBATCH --output=/lustre/research/mfausnau/logs/%x.o%A_%a
#SBATCH --error=/lustre/research/mfausnau/logs/%x.e%A_%a
#SBATCH --partition=nocona
#SBATCH --nodes 1
#SBATCH --cpus-per-task 1
#SBATCH --ntasks-per-node=1
#SBATCH --array=1-500

#
set -eo
shopt -s nullglob


o=$1



folders=($(ls -d cam?-ccd?/"$o"/slice*))
nelements=${#folders[@]}
for (( ii=1; ii<=$nelements; ii++)); do
    if [[ $((ii%500)) -eq ${SLURM_ARRAY_TASK_ID} ]]; then
	cd ${folders[$((ii-1))]}
	echo "running quick_smooth "${folders[$((ii-1))]}
	${PIPELINE_DIR}/util/quick_smooth.py 
	cd ../../../
    fi
done

