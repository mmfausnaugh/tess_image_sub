#!/usr/bin/env bash


#SBATCH --job-name=rms_analysis
#SBATCH --output=${LOG_DIR}/%x.o%j
#SBATCH --error=${LOG_DIR}/%x.e%j
#SBATCH --partition=nocona
#SBATCH --nodes 1
#SBATCH --cpus-per-task 2
#SBATCH --ntasks=16
#SBATCH --account=mfausnau_grp
#SBATCH --ntasks=1

${PIPELINE_DIR}/util/rms_analysis.py  lc/lc_*cleaned
