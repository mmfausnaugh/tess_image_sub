#!/usr/bin/env bash

for i in 1 2 3 4; do 
    for j in 1 2 3 4; do 
	cd "cam$i""_ccd$j"
	pwd

	if [ ! -d lc_discovery ]; then
	    mkdir lc_discovery; 
	fi
	if [ ! -d bkg_phot ]; then
	    mkdir bkg_phot
	fi
	cd bkg_phot
	if [ ! -d lc_discovery ]; then
	    mkdir lc_discovery
	fi
	cd ../
	


	n=$(wc phot.data | awk '{print $1}')
	if [[ $n -gt "0" ]]; then

	    for o in o1a o1b o2a o2b; do 
		if [ -e  "$o" ]; then 
		    cd $o
		    for slice in $(ls -d slice*); do 

			cd $slice/lc_discovery
			for f in $(ls lc_*); do 
			    #ls -d ../../../lc_discovery
			    cat $f >>../../../lc_discovery/"$f" ; 
			done; 
		    		
			cd ../bkg_phot/lc_discovery
			for f in $(ls lc_*); do 
			    #ls -d ../../../../bkg_phot/lc_discovery/
			    cat $f >>../../../../bkg_phot/lc_discovery/"$f" ;
			done; 
	
			#
			cd ../../../; 
		    done
		    cd ../
		fi
		
	    done ; 
	fi
	
	wait
	
	cd lc_discovery
	pwd
	for f in $(ls lc_* | grep -v cleaned | grep -v png); do
	    sort -nuk1 $f > tmp
	    mv tmp $f
	done
	cd ..

	cd bkg_phot/lc_discovery
	pwd
	for f in $(ls lc_* | grep -v cleaned | grep -v png); do
	    sort -nuk1 $f > tmp
	    mv tmp $f
	done
	cd ../../


	cd ../

    done; 
done
