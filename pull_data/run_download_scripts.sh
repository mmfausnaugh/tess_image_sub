#!/usr/bin/env bash

#this script will run the download scripts from MAST in parallel
#Will also check if any files are missing, and rerun the curl command if so
#at the ends, clears away the download scripts

set -euxo

for downloadscript in $(ls hlsp_tica*sh); do
    bash $downloadscript &
done
wait




