#!/usr/bin/env python

import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import numpy  as np
from astropy.io import fits
import sys
from copy import deepcopy

from scipy.ndimage import median_filter
from scipy.interpolate import LSQUnivariateSpline


imlist = np.genfromtxt('dates',usecols=(0),dtype=str)
#TJD = np.genfromtxt('dates',usecols=(1))


#col indices with straps
#it is 14 columns each
strap_indexes = [np.r_[117:131],
                 np.r_[245:261],
                 np.r_[373:389],
                 np.r_[501:517],
                 np.r_[557:573],
                 np.r_[629:645],

                 np.r_[713:724],

                 np.r_[758:774],
                 np.r_[886:902],
                 np.r_[1015:1031],
                 np.r_[1108:1124],
                 np.r_[1236:1252],
                 np.r_[1364:1380],

                 np.r_[1413:1424],

                 np.r_[1492:1508],
                 np.r_[1565:1581],
                 np.r_[1619:1635],
                 np.r_[1748:1764],
                 np.r_[1876:1892],
                 np.r_[2004:2020]
                  ]

#to estimate the local background, it is median of -10/+10 columns around the strap
bkg_indexes = np.array([   [[108,117],[133,142]],
                           [[236,245],[261,270]],
                           [[364,373],[389,398]],
                           [[492,501],[517,526]],
                           [[548,557],[573,582]],
                           [[620,629],[645,654]],
                           [[703,713],[724,734]],
                           [[749,758],[774,783]],
                           [[877,886],[902,911]],
                           [[1006,1015],[1031,1040]],
                           [[1099,1108],[1124,1133]],
                           [[1227,1236],[1252,1261]],
                           [[1355,1364],[1380,1389]],
                           [[1403,1413],[1424,1434]],
                           [[1483,1492],[1506,1517]],
                           [[1556,1565],[1581,1590]],
                           [[1610,1619],[1635,1644]],
                           [[1739,1748],[1764,1773]],
                           [[1867,1876],[1892,1901]],
                           [[1995,2004],[2020,2029]]
                      ])

for ii,im in enumerate(imlist):
#for im in sys.argv[1:]:
    
    f = fits.open('conv_' + im,'update')
    data = f[0].data
#    out  = np.zeros(np.shape(data))
    out2  = deepcopy(data)

    for jj,col_idx  in enumerate(strap_indexes):
        #x, y, knot point locations, order

        bkg_reg1 = bkg_indexes[jj][0]
        bkg_reg2 = bkg_indexes[jj][1]        

        bkg_level = np.median(np.c_[data[:,bkg_reg1[0]:bkg_reg1[1]],
                                    data[:,bkg_reg2[0]:bkg_reg2[1]] ],axis=1)
        for kk in range(len(col_idx)):
            col = np.zeros(2078)
            col[0:524]     = median_filter(data[0:524,     col_idx[kk]],size=100, mode='reflect')
            col[524:1039]  = median_filter(data[524:1039,  col_idx[kk]],size=100, mode='reflect')
            col[1039:1547] = median_filter(data[1039:1547, col_idx[kk]],size=100, mode='reflect')
            col[1547:2078] = median_filter(data[1547:2078, col_idx[kk]],size=100, mode='reflect')

#            out[: ,col_idx[kk]] =  col - bkg_level
            out2[:,col_idx[kk]] = out2[:,col_idx[kk]] - col + bkg_level
        
#        spline = LSQUnivariateSpline(np.r_[0:len(col)],
#                                     col,
#                                     np.r_[1:len(col):124],
#                                     k=3)
#        out_data[:,col_idx] = col - spline(np.r_[0:len(col)])


    #for now, this will become a fits flush when it is dones
    f[0].data = out2
    f.flush()

#    fits.writeto('straps_'+im,out,overwrite=True)
#    fits.writeto('substraps_'+im,out2,overwrite=True)
