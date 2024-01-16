#!/usr/bin/env python
import scipy as sp
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import os
import sys
import glob


duse = os.path.dirname(os.path.abspath(__file__))
t,tess_x,tess_y,tess_z = sp.genfromtxt(os.path.join(duse,'tess_ephem.txt'),
                                       unpack=1,usecols=(0,1,2,3))

def btjd_correction(time_in,ra,dec):
    c = 2.99792458e5 #km/s
    

    interp_x = interp1d(t,tess_x)
    interp_y = interp1d(t,tess_y)
    interp_z = interp1d(t,tess_z)

    ix = interp_x(time_in)
    iy = interp_y(time_in)
    iz = interp_z(time_in)

    tess_position = sp.transpose([ix,iy,iz])

    #ra/dec in radians
    ra_use  = ra*sp.pi/180.0
    dec_use = dec*sp.pi/180.0
    #print(ra,dec)
    #print(ra_use, dec_use)
    source_vector = sp.array([sp.cos(dec_use)*sp.cos(ra_use), 
                              sp.cos(dec_use)*sp.sin(ra_use), 
                              sp.sin(dec_use)])    
    #print(source_vector)
    #print(tess_position)
    #print('{:.3e}'.format(sp.dot(tess_position, source_vector)))
    #assuming tess_position is in kilometers, this gives the correction in days
    dtime =   sp.dot(tess_position, source_vector)/c/86400.0

#    print tess_position
#    print dtime
#    print dtime*24*60
    return time_in + dtime
