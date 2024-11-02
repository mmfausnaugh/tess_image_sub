#!/usr/bin/env bash

#
set -euxo
shopt -s nullglob


o=$1

if [[ $o == 'o1a' ]]; then
    echo "doing o1a"
    image_ref=$(head -1 cam1-ccd1/ref_list)
    image_ref=${image_ref:0:27}
    echo $image_ref
    
    #setup config files.  image ref is the image to align all others too,
    #and to which ref_list gets convolved to match
    echo "running ccd_match_script_em2"
    srun --job-name="setup_ccd_matches" \
	 --output=%x.o%j --error=%x.e%j \
	 --partition=nocona \
	 --nodes 1 --cpus-per-task 1 \
	 --ntasks-per-node=1 \
	 ${PIPELINE_DIR}/setup/ccd_match_script_em2


fi

##link_prf_nums_em2 $o


for i in 1 2 3 4; do 
    for j in 1 2 3 4; do 
	cd "cam$i""-ccd$j"/"$o"
	pwd
	echo "running make_dates in cam$i""-ccd$j"
	for f in ../hlsp_tica_tess*fits; do 
	    mv $f .
	done
	
	echo ${PIPELINE_DIR}
	ls ${PIPELINE_DIR}/setup/make_dates
	srun --job-name="make_dates_cam$i""-ccd$j" \
	     --output=%x.o%j --error=%x.e%j \
	     --partition=nocona \
	     --nodes 1 --cpus-per-task 1 \
	     --ntasks-per-node=1 \
	     ${PIPELINE_DIR}/setup/make_dates &
	cd ../../
    done
done
echo "waiting for dates"
wait

for i in 1 2 3 4; do 
    for j in 1 2 3 4; do 
	cd "cam$i""-ccd$j"/"$o"
	echo "running setup parallel in cam$i""-ccd$j"
	srun --job-name="setup_parallel" \
	     --output=%x.o%j --error=%x.e%j \
	     --partition=nocona \
	     --nodes 1 --cpus-per-task 1 \
	     --ntasks-per-node=1 \
	     ${PIPELINE_DIR}/setup/setup_parallel_em2.sh 256 &
	cd ../../
    done
done
echo "waiting for setup_parallel_em2.sh"
wait

for i in 1 2 3 4; do 
    for j in 1 2 3 4; do 
	cd "cam$i""-ccd$j"/"$o"
	echo "running quick_smooth  in cam$i""-ccd$j"
	for slice in $(ls -d slice*); do 
	    cd $slice
	    srun  --job-name="quick_smooth_cam$i""-ccd$j" \
		 --output=%x.o%j --error=%x.e%j \
		 --partition=nocona \
		 --nodes 1 --cpus-per-task 1 \
		 --ntasks-per-node=1\
		 ${PIPELINE_DIR}/util/quick_smooth.py &
	    cd ..
	done
	echo "waiting for quick smooth"
	wait
	cd ../../
    done
done

