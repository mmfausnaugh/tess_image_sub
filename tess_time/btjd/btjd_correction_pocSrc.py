#!/usr/bin/env python
import scipy as sp
import matplotlib.pyplot as plt
import os
import sys
import glob
import argparse
import spiceypy as s
import poc.configdb as cdb
from poc.poctime import poctime

tjd2utc = poctime('TJD->UTC').convert
s.boddef("TESS", -95)                                                                 
cdb.spice.load()



def btjd_correction(time_in,ra,dec):
    c = 2.99792458e5 #km/s



    utc = tjd2utc(time_in)
    t_spiceypy = s.str2et(utc)

    #s.spkezr returns 6-element array of position and velocity and a scalar light travel time
    #here, I only want the position
    tess_position = sp.array([s.spkezr('TESS', tm, 'J2000', 'NONE', '0')[0] for tm in t_spiceypy ])
    tess_position = tess_position[:,:3]


    #ra/dec in radians
    ra_use  = ra*sp.pi/180.0
    dec_use = dec*sp.pi/180.0
    source_vector = sp.array([sp.cos(dec)*sp.cos(ra), sp.cos(dec)*sp.sin(ra), sp.sin(dec)])    

    #assuming tess_position is in kilometers, this gives the correction in days
    dtime = sp.dot(tess_position, source_vector)/c/86400.0

    print('poc src')
    print tess_position
    print dtime
#    print dtime*24*60
    return time_in + dtime
