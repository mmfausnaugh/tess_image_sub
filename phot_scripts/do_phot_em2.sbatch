#!/usr/bin/env bash


####issue one, need to fill in these variables
### fix by removing environment variables....
#SBATCH --job-name="do_phot"
#SBATCH --output=//lustre/research/mfausnau/logs/%x.o%A_%a
#SBATCH --error=/lustre/research/mfausnau/logs/%x.e%A_%a
#SBATCH --partition=nocona
#SBATCH --nodes 1
#SBATCH --cpus-per-task 1
#SBATCH --ntasks-per-node=1
#SBATCH --array=0-99
#SBATCH --time=0-0:30:00

set -eo

duse=$DATA_DIR
dhome=$(pwd);

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

	if [[ $SLURM_ARRAY_TASK_ID -eq 1 ]]; then
	    if [[ $ii -eq 1 ]]; then
		echo "copying phot.data " $SLURM_ARRAY_TASK_ID
		cp "sector$sector""/cam$cam""_ccd$ccd""/phot.data"   "$duse""/$sectoruse""/cam$cam""-ccd$ccd""/$o"
	    fi
	fi

	cd ${folders[$((ii-1))]}
	echo  "current working  directory:"
	pwd
	for p in $(ls ../psf_file*fits); do
            [[ -e ${p:3:30} ]] || { ln -s $p ; }
        done
	[[ -e psf_table ]] || { ln -s ../psf_table ; }
	    
	if [ ! -d lc ]; then
	    mkdir lc
	fi

	#try to make sure phot.data is copied
	if [[ $ii -lt 101 ]]; then
	    sleep 1
	fi

	[[ -e images.tar ]] && { tar -xf images.tar ; }
	[[ -e kernel_data.tgz ]] && { tar -xzf kernel_data.tgz; }	   

	if [ ! -d bkg_phot ]; then
            mkdir bkg_phot
            cd bkg_phot
            bash $PIPELINE_DIR/setup/make_bkg_phot_dir_em2
	    cd ..
        fi

	
        ${ISIS_DIR}/phot2.csh 


	[[ -e images.tar ]] || { tar -cf images.tar  {interp,conv,bkg}*fits ; }
	[[ -e 'kernel_data.tgz' ]] || {
	    tar -czf kernel_data.tgz {kt_,kc_}*fits 
	}


        rm kt_*fits ;
        rm kc_*fits;

        cd bkg_phot


	if [ ! -d lc ]; then
	    mkdir lc
	fi
	
	[[ -e kernel_data.tgz ]] && { tar -xzf kernel_data.tgz; }

        ${ISIS_DIR}/phot2.csh 
	    
	[[ -e 'kernel_data.tgz' ]] || {
            tar -czf kernel_data.tgz {kt_,kc_}*fits 
        }
	
	
	rm kt_*fits
	rm kc_*fits
	cd ..
	#clean up images after all photometry is done
	rm {interp,conv,bkg}*fits
		
    fi
    
    cd $dhome
done

