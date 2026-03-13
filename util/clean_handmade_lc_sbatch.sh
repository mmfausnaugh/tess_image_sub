#!/usr/bin/env bash


#SBATCH --job-name=clean_lcs 
#SBATCH --output=%x.o%j
#SBATCH --error=%x.e%j 
#SBATCH --partition=nocona 
#SBATCH --nodes 1
#SBATCH --cpus-per-task 1 
#SBATCH --ntasks=1
#SBATCH --time=0-03:00:00

sector=$1
suse=$(printf "%04d"  $1)
cam=$2
ccd=$3
coordfile=$4
indir=$5

echo "check: " $sector $suse $cam $ccd $ccordifle $indir

fluxcal.py --photfile ./phot.data --infiles ${DATA_DIR}/s"$suse"/"cam$cam""-ccd$ccd"/ref.fits 
mv ref_gaussian_psf_flux.txt "$indir"/ref_gaussian_psf_flux.txt

${PIPELINE_DIR}/util/clean_handmade_lc.py  $indir/lc_* --fluxcal "$indir"/ref_gaussian_psf_flux.txt --metafile $4 #--decimal

#rm clean_lcs.o* $LOG_DIR
#rm clean_lcs.e* $LOG_DIR
