#!/usr/bin/env bash

conda activate py312


export DATA_DIR=/lustre/research/mfausnau/data/tica


export PIPELINE_DIR=/lustre/research/mfausnau/software/tess_image_sub/
export ISIS_DIR=/lustre/research/mfausnau/software/isis/

export PIPELINE_PATH=/lustre/research/mfausnau/software/tess_image_sub/bin
export WCSTOOLS_PATH=/home/mfausnau/wcstools-3.9.7/bin
export ISIS_PATH=/lustre/research/mfausnau/software/isis/bin

export PATH="$PIPELINE_PATH:$ISIS_PATH:$WCSTOOLS_PATH:$PATH"
