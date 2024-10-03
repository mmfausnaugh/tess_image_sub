#!/usr/bin/env bash


conda activate py312

export PIPELINE_DIR=/lustre/research/mfausnau/software/tess_image_sub/

export PIPELINE_PATH=/lustre/research/mfausnau/software/tess_image_sub/bin

export DATA_PATH=/lustre/research/mfausnau/data/tica


export PATH="$PIPELINE_PATH:$PATH"
