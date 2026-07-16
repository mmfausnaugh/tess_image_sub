#!/usr/bin/env bash


#SBATCH --job-name=rms_analysis
#SBATCH --output=%x.o%j
#SBATCH --error=%x.e%j
#SBATCH --partition=nocona
#SBATCH --nodes 1
#SBATCH --cpus-per-task 1
#SBATCH --ntasks=1

#SBATCH --time=0-0:30:00

indir=$1
cd $indir
ln -s ../phot.data
cd ..
${PIPELINE_DIR}/util/rms_analysis.py  "$indir"/lc_*cleaned*

#mv rms_analysis.o* $LOG_DIR
#mv rms_analysis.e* $LOG_DIR
