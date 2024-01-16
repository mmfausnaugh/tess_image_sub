#!/usr/bin/env bash

o=$1

if [[ $o == 'o1a' ]]; then
    echo "in o1a"
    image_ref=$(head -1 cam1_ccd1/ref_list)
    image_ref=${image_ref:0:27}
    echo $image_ref
    
    #setup config files.  image ref is the image to align all others too,
    #and to which ref_list gets convolved to match
    ~/image_sub/pipeline/setup/ccd_match_script_em2 $image_ref


fi

link_prf_nums_em2 $o


for i in 1 2 3 4; do 
    for j in 1 2 3 4; do 
	cd "cam$i""_ccd$j"/"$o"
	pwd
	mv ../tess*fits .
	mv ../wcs_diags2/ .
	make_dates &	
	cd ../../
    done
done
wait


for i in 1 2 3 4; do 
    for j in 1 2 3 4; do 
	cd "cam$i""_ccd$j"/"$o"
	setup_parallel_em2.sh 192
	cd ../../
    done
done
wait

for i in 1 2 3 4; do 
    for j in 1 2 3 4; do 
	cd "cam$i""_ccd$j"/"$o"
	for slice in $(ls -d slice*); do 
	    cd $slice
	    python ~/image_sub/pipeline/util/quick_smooth.py &
	    cd ..
	done
	wait
	cd ../../
    done
done

