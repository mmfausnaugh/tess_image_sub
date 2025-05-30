#!/usr/bin/env bash


#SBATCH --job-name=rms_analysis
#SBATCH --output=%x.o%j
#SBATCH --error=%x.e%j
#SBATCH --partition=nocona
#SBATCH --nodes 1
#SBATCH --cpus-per-task 2
#SBATCH --ntasks=16
#SBATCH --account=mfausnau_grp
#SBATCH --ntasks=1

${PIPELINE_DIR}/util/rms_analysis.py  lc/lc_*cleaned

mv rms_analysis.o* $LOG_DIR
mv rms_analysis.e* $LOG_DIR
