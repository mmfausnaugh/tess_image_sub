#!/usr/bin/env bash

awk '{print $2" "$3}' $1 > tmp.coords
xy2sky ../ref.fits @tmp.coords > "$1"_skycoords.txt
