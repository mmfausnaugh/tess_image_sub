#!/usr/bin/env bash


#SBATCH --job-name=clean_lcs 
#SBATCH --output=%x.o%j
#SBATCH --error=%x.e%j 
#SBATCH --partition=nocona 
#SBATCH --nodes 1
#SBATCH --cpus-per-task 2 
#SBATCH --ntasks=16

for i in 1 2 3 4; do
    for j in 1 2 3 4; do
	cd "cam$i""-ccd$j"
	srun --ntasks=1 --cpus-per-task=${SLURM_CPUS_PER_TASK} --account=${ACCOUNT} fluxcal.py --photfile "$1"/phot.data --infiles ref.fits &
	cd ..
    done
done
wait

for i in 1 2 3 4; do
    for j in 1 2 3 4; do
	cd "cam$i""-ccd$j"
	mv ref_gaussian_psf_flux.txt "$1"
	srun --ntasks=1 --cpus-per-task=${SLURM_CPUS_PER_TASK} --account=${ACCOUNT} ${PIPELINE_DIR}/util/clean_lc.py  "$1"/lc_* --fluxcal "$1"/ref_gaussian_psf_flux.txt &
	cd ..
    done
done

wait

#mv clean_lc.o* $LOG_DIR
#mv clean_lc.e* $LOG_DIR
