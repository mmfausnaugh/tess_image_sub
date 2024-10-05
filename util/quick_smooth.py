#!/usr/bin/env python

import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import numpy as np
from scipy.ndimage import gaussian_filter
from astropy.io import fits

imlist = np.genfromtxt('dates',usecols=(0),dtype=str) 

for im in np.nditer(imlist):
    
    if os.path.isfile('interp_'+str(im) ):
        continue
    #    data = fits.open(im)[0].data
    try:
        fin = fits.open( str(im) )
    except:
        continue
    data = fin[0].data
#    sdata = gaussian_filter(data,0.45,mode='constant')
    sdata = gaussian_filter(data,0.9,mode='constant')
#    sdata = gaussian_filter(data,1.8,mode='constant')

#    fits.writeto('interp_'+im,sdata,overwrite=True)

    hdu0 = fits.PrimaryHDU(data=sdata, header=fin[0].header)
    hdu1 = fin[1]
    
    hdu_list = fits.HDUList([hdu0,hdu1])
    hdu_list.writeto('interp_' + str(im) , checksum=True)
