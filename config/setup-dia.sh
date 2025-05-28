#!/usr/bin/env bash

#this script assumes you have:

#conda installed
#an environment called `py312`.  It should match the .yaml file in this directory
#wcstools-3.9.7 installed in your home directory

conda activate py312


export DATA_DIR=/lustre/research/mfausnau/data/tica


export PIPELINE_DIR=/lustre/research/mfausnau/software/tess_image_sub/
export ISIS_DIR=/lustre/research/mfausnau/software/isis/

export PIPELINE_PATH=/lustre/research/mfausnau/software/tess_image_sub/bin
export WCSTOOLS_PATH=${HOME}/wcstools-3.9.7/bin
export ISIS_PATH=/lustre/research/mfausnau/software/isis/bin
export PYTHONPATH=/lustre/research/mfausnau/software/
export PATH="$PIPELINE_PATH:$ISIS_PATH:$WCSTOOLS_PATH:$PATH"

export LOG_DIR=/lustre/scratch/mfausnau/logs

export NCORES=512

export ACCOUNT="mfausnau_grp"
