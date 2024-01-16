import scipy as sp
from astropy.io import fits
import os
import sys
import matplotlib.pyplot as plt
from copy import deepcopy

from scipy.ndimage import median_filter,convolve1d
from scipy.interpolate import splrep,splev,UnivariateSpline


#tunning params--how strong the gradient should be to mask from spline
#fit, how msooth the spline should be
mask_thresh = 1000
smooth_factor=1.5e7
weight_scale = 1.e-8

def vertical_gradient_mask(im):                                                           
    abs_diffs = abs(convolve1d(im, [-1.,0.,1.],axis=0,mode='reflect'))
    return abs_diffs > mask_thresh

def horizontal_gradient_mask(im):                                                           
    abs_diffs = abs(convolve1d(im, [-1.,0.,1.],axis=1,mode='reflect'))
    return abs_diffs > mask_thresh


strap_indexes = sp.r_[sp.r_[117:131],                                                          
                      sp.r_[245:261],                                                          
                      sp.r_[373:389],                                                          
                      sp.r_[501:517],                                                          
                      sp.r_[557:573],                                                          
                      sp.r_[629:645],                                                          
                      sp.r_[758:774],                                                          
                      sp.r_[886:902],                                                          
                      sp.r_[1015:1031],                                                        
                      sp.r_[1108:1124],                                                        
                      sp.r_[1236:1252],                                                        
                      sp.r_[1364:1380],                                                        
                      sp.r_[1492:1508],                                                        
                      sp.r_[1565:1581],                                                        
                      sp.r_[1619:1635],                                                        
                      sp.r_[1748:1764], 
                      sp.r_[1876:1892],                                                        
                      sp.r_[2004:2020]                                                         
                  ] 



imlist = sp.genfromtxt('dates',usecols=(0),dtype=str)


save_all = True

#15 sub stamps, with slices for col,row
col_subs = [ [44,540],[540,1069],[1069,1598],[1598,2095] ]
row_subs = [ [9,524],[524,1039],[1039,1554],[1554,2048] ]
#if averaging over 5 columns, should avoid the edges of each subframe
sub_col_edges = [44,45,536, 537, 538,539,1067,1068,1069,1070,1596,1597,1598,1599,2093,2094]


filter_size = 30


for ii,im in enumerate(imlist):
    print(im)
    f = fits.open('conv_'+im)
    data = f[0].data
    bkg = sp.zeros( (2078,2136) )

    for jj in range(44,2096):
        for row_sub in row_subs:
            if jj in strap_indexes or jj in sub_col_edges:
                data_use = deepcopy(data[row_sub[0]:row_sub[1],jj])
                m = vertical_gradient_mask(data_use)
                weights = sp.ones(len(data_use))
                weights[m] = weight_scale
            else:
                data_use = deepcopy(data[row_sub[0]:row_sub[1],jj-2:jj+2])
                m = vertical_gradient_mask(data_use)

                #v1,v2 = sp.percentile(sp.ravel(data_use),[10,90])
                #plt.imshow(data_use,vmin=v1,vmax=v2,aspect='equal')
                #                    for kk in range(sp.shape(data_use)[1]):
#                if jj == 1514:
#                    plt.figure()
#                    for kk in range(sp.shape(data_use)[1]):
#                        plt.plot(sp.r_[0:len(data_use[0:,kk])],data_use[:,kk],'o')
                #plt.errorbar(sp.r_[0:len(data_use)],data_use,1./(weights*1.e3),fmt='o')
               
                data_use = sp.mean(data_use,axis=1)
#                plt.plot(sp.r_[0:len(data_use)],data_use,'ko')

                weights = sp.ones(len(data_use))
                for kk in range(sp.shape(m)[1]):
                    weights[m[:,kk]] = weight_scale



#            if jj == 1514:
#                print(row_sub[0],row_sub[1],len(sp.where(m)[0]))


            spl = UnivariateSpline(sp.r_[0:len(data_use)],
                                   data_use,
                                   w=weights,
                                   s=smooth_factor)            
            bkg[row_sub[0]:row_sub[1],jj]= spl(sp.r_[0:len(data_use)])
#            if jj == 1514:
#                plt.figure()
#                plt.plot(data_use,'ko')
#                plt.plot(bkg[row_sub[0]:row_sub[1],jj],'r')
#            
            if any(sp.isnan(bkg[row_sub[0]:row_sub[1],jj])):
                print(len(sp.where(m)[0]), any(sp.isnan(bkg[row_sub[0]:row_sub[1],jj])) )

    out = data - bkg
    if save_all:
        fits.writeto('conv2a_'+im, out)
        fits.writeto('bkga_'+im, bkg)


    bkg = sp.zeros( (2078,2136) )
    for jj in range(9,2048):
        for col_sub in col_subs:
            data_use = deepcopy(out[jj-2:jj+2,col_sub[0]:col_sub[1]])
            m = horizontal_gradient_mask(data_use)

            data_use = sp.mean(data_use,axis=0)

            weights = sp.ones(sp.shape(data_use))
            for kk in range(sp.shape(m)[0]):
                weights[m[kk,:]] = weight_scale
                    

            spl = UnivariateSpline(sp.r_[0:len(data_use)],
                                   data_use,
                                   w = weights,
                                   s=smooth_factor)
            
            bkg[jj,col_sub[0]:col_sub[1]] = spl(sp.r_[0:len(data_use)])

    out = out - bkg



    if save_all:
        fits.writeto('conv2b_'+im, out)
        fits.writeto('bkgb_'+im, bkg)
    else:
        f[0].data = out
        f.flush()

#plt.show()
