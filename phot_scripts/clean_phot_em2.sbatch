#!/usr/bin/env bash


####issue one, need to fill in these variables
### fix by removing environment variables....
#SBATCH --job-name="clean_phot"
#SBATCH --output=//lustre/research/mfausnau/logs/%x.o%A_%a
#SBATCH --error=/lustre/research/mfausnau/logs/%x.e%A_%a
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
#not needed here, check against all orbit segments
#o=$4

dtarget=$DATA_DIR"/$sectoruse""/cam$2""-ccd$3"


infiles=( $(ls "$dhome""/sector$1""/cam$2""_ccd$3"/lc/lc_* | grep -v *png | grep -v *cleaned | awk -F"/" '{print $NF}' )) 
nelements=${#infiles[@]}
echo $nelements
for (( ii=1; ii<=$nelements; ii++ )); do
    if [[ $SLURM_ARRAY_TASK_ID -gt $nelements ]]; then
	exit
    elif [[ $((ii%500)) -eq $SLURM_ARRAY_TASK_ID ]]; then


	f=${infiles[$((ii-1))]}
	echo $f  $ii  $SLURM_ARRAY_TASK_ID

        sort -nuk1 "$dhome""/sector$1""/cam$2""_ccd$3""/lc"/$f > "$f"_tmp
        mv "$f"_tmp "$dhome""/sector$1""/cam$2""_ccd$3""/lc"/$f
        sort -nuk1 "$dhome""/sector$1""/cam$2""_ccd$3""/bkg_phot/lc"/$f > "$f"_tmp2
        mv "$f"_tmp2 $f

	
	ncheck=$(wc "$dhome""/sector$1""/cam$2""_ccd$3""/lc"/$f | awk '{print $1}')
	ncheck2=$(wc "$dhome""/sector$1""/cam$2""_ccd$3""/bkg_phot/lc/"$f | awk '{print $1}')
	printf "%20s %20s\n" "N_lc_home"  "N_bkg_lc_home"
	printf "%20s %20s\n" $ncheck $ncheck2


	#make sure that all lines in /data/tess/image_sub have been concated
	nlines=0
	cd "$dtarget"
	for o in o1a o1b o2a o2b; do
	    cd $o
	    for slice in $(ls -d slice*); do
		cd $slice
		if [ -e "lc/$f" ]; then
		    jj=$(wc "lc/$f" | awk '{print $1}')
		    let nlines=$(($nlines + $jj))
		fi
		cd ..
	    done
	    cd ..
	done

       
	printf "%20s %20s %20s\n" "N_lc_home" "N_bkg_lc_home"  "N_lines_found_in_slices"
	printf "%20s %20s %20s\n" $ncheck   $ncheck2   $nlines
    	echo "all the counting is done"
	if [[ $ncheck == $ncheck2 ]]; then
	    echo "equal background and lc data points"
	    if [[ $ncheck == $nlines ]]; then
		echo "$f passed, deleted from slice directories"
		for o in o1a o1b o2a o2b; do 
		    cd $o
		    for slice in $(ls -d slice*); do
			cd $slice
			rm lc/"$f"
			if [ -d bkg_phot ]; then
			    cd bkg_phot
			    rm lc/"$f"
			    cd ../
			fi
			cd ../
		    done
		    cd ..
		done
		
	    fi
	fi
	
    	echo "last fi clause"
	
    fi
    
    cd $dhome
    
done



