#!/usr/bin/env bash

awk '{print "circle "$1+1" "$2+1" 0.5"}' phot.data > phot.reg
awk '{print "circle "$1+1" "$2+1" 4"}' phot.data >> phot.reg
awk '{print "circle "$1+1" "$2+1" 8"}' phot.data >> phot.reg
awk '{print "circle "$1+1" "$2+1" 80"}' phot.data >> phot.reg
