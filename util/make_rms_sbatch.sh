#!/usr/bin/env bash


#SBATCH --job-name=make_rms
#SBATCH --output=%x.o%j
#SBATCH --error=%x.e%j
#SBATCH --partition=nocona
#SBATCH --nodes 1
#SBATCH --cpus-per-task 1
#SBATCH --ntasks=1
#SBATCH --account=mfausnau_grp
#SBATCH --ntasks=1

python ${PIPELINE_DIR}/util/make_rms.py  $1 

mv make_rms.o* ${LOG_DIR}/
mv make_rms.e* ${LOG_DIR}/
