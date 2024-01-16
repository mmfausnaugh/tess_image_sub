#!/bin/sh
## Run interp on multiple processing units
## $1 - field number
## $2 - sector number
## $3 - number of processing units to use
## $4 - reference fits file
## e.g. bash do_parallel_interp.sh 19 47 32 rot_cam4-00196100.fits

# Make slice directories with the corresponding dates file
python make_interp_parallel.py $1 $2 $3

cd fie*$1/sec*$2
# Update the reference fits file
sed "s@REF.FITS@$4@" process_config_template > process_config

for (( ii=0 ; ii<$3 ; ii++ )); do
    slice=$(printf "slice%02d" $ii)
    # For each slice create the process_config files
    sed "s@\sDirectory@$slice/  Directory@" process_config | \
        sed "s@dates\sDates@$slice/dates  Dates@" > $slice/process_config

    # Create soft links to the field FITS files
    cd $slice
    for f in $(awk '{print $1}' dates); do ln -s ../$f; done
    cd ..
done

## Run interp
for (( ii=0 ; ii<$3 ; ii++ )); do
    cd $(printf "slice%02d" $ii)
    ~/../faus/isis/interp.match2 & 
    cd ..
done

wait

printf "\n...we are done!\n"
