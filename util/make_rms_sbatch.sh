#!/usr/bin/env bash


#SBATCH --job-name=make_rms
#SBATCH --output=${LOG_DIR}/%x.o%j
#SBATCH --error=${LOG_DIR}/%x.e%j
#SBATCH --partition=nocona
#SBATCH --nodes 1
#SBATCH --cpus-per-task 2
#SBATCH --ntasks=16
#SBATCH --account=mfausnau_grp
#SBATCH --ntasks=1

python ${PIPELINE_DIR}/util/make_rms.py  $1
