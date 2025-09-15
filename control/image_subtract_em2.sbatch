#!/usr/bin/env bash

####issue one, need to fill in these variables
### fix by removing environment variables....
#SBATCH --job-name="image_subtract" 
#SBATCH --output=//lustre/research/mfausnau/logs/%x.o%A_%a
#SBATCH --error=/lustre/research/mfausnau/logs/%x.e%A_%a
#SBATCH --partition=nocona 
#SBATCH --nodes 1
#SBATCH --cpus-per-task 1 
#SBATCH --ntasks-per-node=1
#SBATCH --array=1-500

set -eo
segment=$1
sector=$(pwd | awk -F/ '{print $7}')


folders=($(ls -d cam?-ccd?/"$segment"/slice*))
nelements=${#folders[@]}
echo $nelements 
echo "SLURM_ARRAY_TASK_ID" $SLURM_ARRAY_TASK_ID
for (( ii=1; ii<=$nelements; ii++ )); do
    if [[ $((ii%500)) -eq $SLURM_ARRAY_TASK_ID ]]; then

	echo $ii 
	cd ${folders[$((ii-1))]} 
	pwd 2>&1 
	${ISIS_DIR}/subtract.csh 
	${PIPELINE_DIR}/util/correct_straps.py 
	${PIPELINE_DIR}/util/median_filter_diff_row_col.py 
	cd ../../../ 

    fi
done

####issue two, need to concat the log files
#could I use ${SBATCH_JOB_NAME}.o${SLURM_JOB_ID} ???
#yes, I think so; turn off slurm logging, and redirect everything ot a specified file
####issue three, need a script to kill the jobs??
##I don't think so, just need to do `scancel ${SBATCH_JOB_NAME}
