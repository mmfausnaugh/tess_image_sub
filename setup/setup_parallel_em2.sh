#!/bin/sh
## Setup a given directory ready for image sub/photometry 
#for multiple processing units
## Arguments: 
## $1 - number of processing units to use

# Make slice directories with the corresponding dates file

set -euo

python "${PIPELINE_DIR}/setup/"make_parallel.py $1


for (( ii=0 ; ii<$1 ; ii++ )); do
    slice=$(printf "slice%04d" $ii)
    if [ -d $slice ]; then 
	# For each slice create the process_config files
	sed "s@\sDirectory@$slice/  Directory@" process_config | \
            sed "s@dates\sDates@$slice/dates  Dates@" > $slice/process_config

	# Create soft links to the field FITS files
	cd $slice
	for f in $(awk '{print $1}' dates); do
	    [[ -e $f ]] || {
		ln -s ../$f;
	    }
	done
	cd ..
    fi
done

