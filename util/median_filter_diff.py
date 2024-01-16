import scipy as sp
from astropy.io import fits
import os
import sys

from copy import deepcopy

from scipy.ndimage import median_filter,convolve1d
from scipy.interpolate import splrep,splev


#did some experiments trying to mask out star residuals based on sharp
#gradients.  some succes, but limited
mask_thresh = 1000
def vertical_gradient_mask(im):                                                           
    abs_diffs = abs(convolve1d(im, [-1.,1.],axis=0,mode='reflect'))
    return abs_diffs > mask_thresh

def horizontal_gradient_mask(im):                                                           
    abs_diffs = abs(convolve1d(im, [-1.,1.],axis=1,mode='reflect'))
    return abs_diffs > mask_thresh


imlist = sp.genfromtxt('dates',usecols=(0),dtype=str)

col_subs = [ [44,540],[540,1069],[1069,1598],[1598,2095] ]                                                                                                                
row_subs = [ [9,524],[524,1039],[1039,1554],[1554,2048] ] 

#save_all = True


#2D filter, just pass this as an integer to median_filter
filter_size = 15


for ii,im in enumerate(imlist):
    f = fits.open('conv_'+im)
    data = f[0].data
    bkg = sp.zeros( (2078,2136) )

    for row_sub in row_subs:
        for col_sub in col_subs:
            data_use = deepcopy(data[row_sub[0]:row_sub[1],
                                     col_sub[0]:col_sub[1]])
            #m = vertical_gradient_mask(data_use)
            #data_use[m] = sp.nan
            bkg[row_sub[0]:row_sub[1],
                col_sub[0]:col_sub[1]] = median_filter(data_use,
                                                       size=filter_size,
                                                       mode='reflect')
            bkg[sp.isnan(bkg)] = 0.0


    out = data - bkg
    f[0].data = out
    f.flush()
    fits.writeto('bkg_'+im, bkg)
