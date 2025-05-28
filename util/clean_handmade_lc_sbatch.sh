#!/usr/bin/env bash


#SBATCH --job-name=clean_lcs 
#SBATCH --output=${LOG_DIR}/%x.o%j
#SBATCH --error=${LOG_DIR}/%x.e%j 
#SBATCH --partition=nocona 
#SBATCH --nodes 1
#SBATCH --cpus-per-task 2 
#SBATCH --ntasks=16
#SBATCH --account=mfausnau_grp
#SBATCH --ntasks=1

sector=$1
suse=$(printf "%04d"  $1)
cam=$2
ccd=$3
coordfile=$4


fluxcal.py --photfile ./phot.data --infiles ${DATA_DIR}/s"$suse"/"cam$cam""-ccd$ccd"/ref.fits 
mv ref_gaussian_psf_flux.txt lc

${PIPELINE_DIR}/util/clean_handmade_lc.py  lc/lc_* --fluxcal lc/ref_gaussian_psf_flux.txt --metafile $4
