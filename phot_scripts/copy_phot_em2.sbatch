#!/usr/bin/env bash


####issue one, need to fill in these variables
### fix by removing environment variables....
#SBATCH --job-name="copy_phot"
#SBATCH --output=//lustre/research/mfausnau/logs/%x.o%A_%a
#SBATCH --error=/lustre/research/mfausnau/logs/%x.o%A_%a
#SBATCH --partition=nocona
#SBATCH --nodes 1
#SBATCH --cpus-per-task 1
#SBATCH --ntasks-per-node=1
#SBATCH --array=1-500
#SBATCH --time=90

set -eo

duse=$DATA_DIR
dhome=$(pwd);

sector=$1
sectoruse=$(printf "s%04d" $1)
echo "sector use:"  $sectoruse
cam=$2
ccd=$3
o=$4

dtarget=$DATA_DIR"/$sectoruse""/cam$2""-ccd$3"


folders=($(ls -d "$duse"/"$sectoruse"/cam$2-ccd$3/"$o"/slice*))
nelements=${#folders[@]}

for (( ii=1; ii<=$nelements; ii++ )); do
    if [[ $SLURM_ARRAY_TASK_ID -eq 1 ]]; then
	[[ -d "$dhome""/sector$1""/cam$2""_ccd$3""/lc" ]] || { mkdir -p "$dhome""/sector$1""/cam$2""_ccd$3""/lc" ; }
	[[ -d "$dhome""/sector$1""/cam$2""_ccd$3""/bkg_phot" ]] || { mkdir -p "$dhome""/sector$1""/cam$2""_ccd$3""/bkg_phot" ; }
	[[ -d "$dhome""/sector$1""/cam$2""_ccd$3""/bkg_phot/lc" ]] || { mkdir -p "$dhome""/sector$1""/cam$2""_ccd$3""/bkg_phot/lc" ; }

    fi
    sleep 3
    
    if [[ $((ii%500)) -eq $SLURM_ARRAY_TASK_ID ]]; then
	
	cd ${folders[$((ii-1))]}
	cd lc
	echo "current directory"
	pwd

	
	for f in $(ls lc_*); do
	    cat $f >> "$dhome""/sector$1""/cam$2""_ccd$3""/lc/$f" 
	done

	cd ../bkg_phot/lc
        for f in $(ls lc_*); do
            cat $f >> "$dhome""/sector$1""/cam$2""_ccd$3""/bkg_phot/lc/$f" 
            #cat $f >> "$dtarget""/bkg_phot/lc/$f" &
        done
	
    fi
    
    cd $dhome
    
    ##if [[ $SLURM_ARRAY_TASK_ID -eq $nelements ]]; then
    ##	sleep 60
    ##	cd lc
    ##	for f in $(ls lc_* | grep -v cleaned | grep -v png); do
    ##        sort -nuk1 $f > tmp
    ##        mv tmp $f
    ##	done
    ##	cd ../bkg_phot/lc
    ##	for f in $(ls lc_* | grep -v cleaned | grep -v png); do
    ##        sort -nuk1 $f > tmp
    ##        mv tmp $f
    ##	done    
    ##fi
done


