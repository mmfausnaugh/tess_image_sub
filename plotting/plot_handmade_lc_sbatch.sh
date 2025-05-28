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

coordfile=$1



${PIPELINE_DIR}/plotting/plot_cleaned_lc.py  lc/lc_*cleaned --mag --bkg --metafile $coordfile
