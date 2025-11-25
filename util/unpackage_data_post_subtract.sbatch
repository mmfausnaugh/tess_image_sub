#!/usr/bin/env bash


####issue one, need to fill in these variables
### fix by removing environment variables....
#SBATCH --job-name="unpackage_data"
#SBATCH --output=//lustre/research/mfausnau/logs/%x.o%A_%a
#SBATCH --error=/lustre/research/mfausnau/logs/%x.e%A_%a
#SBATCH --partition=nocona
#SBATCH --nodes 1
#SBATCH --cpus-per-task 1
#SBATCH --ntasks-per-node=1
#SBATCH --array=0-99
#SBATCH --time=0-1:00:00

set -o

duse=$DATA_DIR

sector=$1
sectoruse=$(printf "s%04d" $1)
echo "sector use:" $sectoruse
cam=$2
ccd=$3
o=$4

folders=($(ls -d "$duse"/"$sectoruse"/cam$2-ccd$3/"$o"/slice*))
nelements=${#folders[@]}

for (( ii=1; ii<=$nelements; ii++ )); do
    #modulos will be 1 to 99, 0  never 100
    if [[ $((ii%100 )) -eq $SLURM_ARRAY_TASK_ID ]]; then

	
        cd ${folders[$((ii-1))]}
        echo  "current working  directory:"
        pwd


	[[ -e images.tar ]] && { tar -xf images.tar  {interp,conv,bkg}*fits ; }
        [[ -e 'kernel_data.tgz' ]] && {
            tar -xzf kernel_data.tgz {kt_,kc_}*fits
        }
	
	cd bkg_phot
	
        [[ -e 'kernel_data.tgz' ]] && {
            tar -xzf kernel_data.tgz {kt_,kc_}*fits
        }
		

    fi
done
