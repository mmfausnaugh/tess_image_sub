#!/usr/bin/env bash


#SBATCH --job-name=plot_handmade_lc 
#SBATCH --output=%x.o%j
#SBATCH --error=%x.e%j 
#SBATCH --partition=nocona 
#SBATCH --nodes 1
#SBATCH --cpus-per-task 2 
#SBATCH --ntasks=16
#SBATCH --account=mfausnau_grp
#SBATCH --ntasks=1
#SBATCH --time=0-03:00:00

coordfile=$1
indir=$2


${PIPELINE_DIR}/plotting/plot_cleaned_lc.py  "$indir"/lc_*cleaned --mag --bkg --metafile $coordfile --decimal
