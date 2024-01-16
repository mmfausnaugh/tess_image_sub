#!/usr/bin/env bash

concat_lc.sh
wait
for i in 1 2 3 4; do 
    for j in 1 2 3 4; do
	cd "cam$i""_ccd$j"/lc_discovery
	mv ../phot.data .
	fluxcal.py --infiles ../ref.fits --photfile phot.data &
	cd ../../
    done
done
wait

for i in 1 2 3 4; do 
    for j in 1 2 3 4; do
	cd "cam$i""_ccd$j"
	clean_lc.py lc_discovery/lc_* --fluxcal lc_discovery/ref_gaussian_psf_flux.txt &
	cd ../
    done
done
    
wait

for i in 1 2 3 4; do 
    for j in 1 2 3 4; do
	cd "cam$i""_ccd$j"
	rm -fr lc_discovery/*png
	plot_TNS_cleaned_lc.py lc_discovery/lc_*cleaned --bkg --mag &
	cd ../
    done
done
    
wait
