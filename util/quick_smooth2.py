#!/usr/bin/env python
import scipy as sp
from scipy.ndimage import gaussian_filter
from astropy.io import fits
import os

imlist = sp.genfromtxt('dates',usecols=(0),dtype=str) 

for im in imlist:
    print(im)
    #if os.path.isfile('interp_'+im):
    #    continue
    #    data = fits.open(im)[0].data
    try:
        fin = fits.open('interp_'+im)
    except:
        continue
    data = fin[0].data
#    sdata = gaussian_filter(data,0.45,mode='constant')
    sdata = gaussian_filter(data,0.9,mode='constant')
#    sdata = gaussian_filter(data,1.8,mode='constant')

    fits.writeto('interp_'+im,sdata,overwrite=True)

    #hdu0 = fits.PrimaryHDU(data=sdata, header=fin[0].header)
    #hdu1 = fin[1]
    
    #hdu_list = fits.HDUList([hdu0,hdu1])
    #hdu_list.writeto('interp_'+im, checksum=True)
