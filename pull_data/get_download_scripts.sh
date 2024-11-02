#!/usr/bin/env bash

#this script will pull the latest download scripts from MAST
#the MAST scripts use curl to grab the data

set -euxo

sector=$1
segment=$2

sectoruse=$(printf "%04d" $sector)

urlstem="https://archive.stsci.edu/hlsps/tica/bundles/"


dstem=$DATA_DIR
target="$dstem""/s$sectoruse"

if [[ -d $target ]]; then
    cd $target
else
    mkdir -p $target
    cd $target
fi


for ii in 1 2 3 4; do
    for jj in 1 2 3 4; do
	urluse="$urlstem""s""$sectoruse""/hlsp_tica_tess_ffi_s""$sectoruse""-""$segment""-cam""$ii""-ccd""$jj""_tess_v01_ffis.sh"

	wget $urluse

    done
done
