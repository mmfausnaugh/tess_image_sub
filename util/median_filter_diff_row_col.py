import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import numpy as np
from astropy.io import fits
import sys

from copy import deepcopy

from scipy.ndimage import median_filter,convolve1d
from scipy.interpolate import splrep,splev


mask_thresh = 1000

def vertical_gradient_mask(im):                                                           
    abs_diffs = abs(convolve1d(im, [-1.,1.],axis=0,mode='reflect'))
    return abs_diffs > mask_thresh

def horizontal_gradient_mask(im):                                                           
    abs_diffs = abs(convolve1d(im, [-1.,1.],axis=1,mode='reflect'))
    return abs_diffs > mask_thresh


imlist = np.genfromtxt('dates',usecols=(0),dtype=str)


#save_all = True

#15 sub stamps, with slices for col,row
col_subs = [ [44,540],[540,1069],[1069,1598],[1598,2095] ]
row_subs = [ [9,524],[524,1039],[1039,1554],[1554,2048] ]

filter_size = 30


for ii,im in enumerate(imlist):

    f = fits.open('conv_'+im,'update')
    data = f[0].data
    bkg = np.zeros( (2078,2136) )

    for row_sub in row_subs:
        for col_sub in col_subs:
            data_use = deepcopy(data[row_sub[0]:row_sub[1],
                                     col_sub[0]:col_sub[1]])
            #m = vertical_gradient_mask(data_use)
            #data_use[m] = np.nan
            bkg[row_sub[0]:row_sub[1],
                col_sub[0]:col_sub[1]] = median_filter(data_use,
                                                       size=(filter_size,1),
                                                       mode='reflect')
            bkg[np.isnan(bkg)] = 0.0


    out = data - bkg

    bkg2 = np.zeros( (2078,2136) )
    for row_sub in row_subs:
        for col_sub in col_subs:
            data_use = deepcopy(out[row_sub[0]:row_sub[1],
                                    col_sub[0]:col_sub[1]])
            #m = horizontal_gradient_mask(data_use)
            #data_use[m] = np.nan

            bkg2[row_sub[0]:row_sub[1],
                 col_sub[0]:col_sub[1]] = median_filter(data_use,
                                                        size=(1,filter_size),
                                                        mode='reflect')
            bkg2[np.isnan(bkg)] = 0.0

    out = out - bkg2



    fits.writeto('bkg_'+im, bkg + bkg2)
