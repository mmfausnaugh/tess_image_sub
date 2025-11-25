#!/usr/bin/env bash

####issue one, need to fill in these variables
### fix by removing environment variables....
#SBATCH --job-name="make_dates"
#SBATCH --output=/lustre/research/mfausnau/logs/%x.o%A_%a
#SBATCH --error=/lustre/research/mfausnau/logs/%x.e%A_%a
#SBATCH --partition=nocona
#SBATCH --nodes 1
#SBATCH --cpus-per-task 1
#SBATCH --ntasks-per-node=1
#SBATCH --array=1-16

#
set -eo
shopt -s nullglob


o=$1

if [[ $o == 'o1a' ]]; then
    if [[ ${SLURM_ARRAY_TASK_ID} -eq 1 ]]; then
	echo "doing o1a"
	image_ref=$(head -1 cam1-ccd1/ref_list)
	image_ref=${image_ref:0:27}
	echo $image_ref
    
	#setup config files.  image ref is the image to align all others too,
	#and to which ref_list gets convolved to match
	echo "running ccd_match_script_em2"
	#just copying files, doesn't need to be run more than once
	#srun --job-name="setup_ccd_matches" \
	   # --output=${LOG_DIR}/%x.o%j --error=${LOG_DIR}/%x.e%j \
	   # --partition=nocona \
	   # --account=${ACCOUNT} \
	   # --nodes 1 --cpus-per-task 1 \
	   # --ntasks-per-node=1 \
	 ${PIPELINE_DIR}/setup/ccd_match_script_em2
    fi
fi
sleep 3

echo $o
#link at the segment level directory (o1a, o1b, o2a, or o2b)
if [[ ${SLURM_ARRAY_TASK_ID} -eq 1 ]]; then
    link_prf_nums_em2 $o
fi
sleep 3



#folders=($(ls -d cam?-ccd?/"$o"))
#nelements=${#folders[@]}

cam=$((  (${SLURM_ARRAY_TASK_ID}-1)/4 +1))
ccd=$((  (${SLURM_ARRAY_TASK_ID}-1)%4 +1))
cd "cam$cam""-ccd$ccd"/"$o"
pwd
echo "running make_dates in cam$i""-ccd$j"
#moved to downlowd scripts
#for f in ../hlsp_tica_tess*fits; do 
#    mv $f .
#done

#echo ${PIPELINE_DIR}
#ls ${PIPELINE_DIR}/setup/make_dates
${PIPELINE_DIR}/setup/make_dates 
echo "running setup_parallel_em2"
${PIPELINE_DIR}/setup/setup_parallel_em2.sh $NCORES 
echo "finished!"
