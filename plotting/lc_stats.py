#!/usr/bin/env python
import scipy as sp
from scipy.stats import sigmaclip
from scipy.ndimage import median_filter
import matplotlib.pyplot as plt
from astropy.io import ascii
from astropy.time import Time
import os
import sys

from tess_time.cut_ffi.cut_data import cut_data

#def cut_data(x,y,z):
#    s4_time_cut = [1421.209, 1424.4]     
#    m = ( x > s4_time_cut[0]) & ( x < s4_time_cut[1])
#    x,y,z = x[~m], y[~m], z[~m]
#
#    tjd_cut = sp.genfromtxt('/pdo/users/faus/image_sub/pipeline/time/cut_ffi/cut_fin_data',usecols=(2))
#    m = []
#    for ii,epoch in enumerate(x):
#        if any(sp.isclose(tjd_cut,epoch, atol=1.e-4)):
#            m.append(ii)
#    return sp.delete(x,m), sp.delete(y,m), sp.delete(z,m)

def med_filter(y):
    med = sp.zeros(len(y))

    for i in range(len(y)):
        med[i] = sp.median(y[ max(i-10,0): min(i+10,len(y)-1)])

    return y - med,med

def stats(x,z,y,y0,ax1,ax2):

#    print '{:4.2e} {:4.2e} {:}'.format(y0,bkg, area)
#    print '  {:5.3f} +/- {:5.3f}'.format(sp.mean(clip_y),sp.std(clip_y))
#    print '  clipped std/y0: {:4.2e}'.format(sp.std(clip_y)/y0)
#    print '  bkg limit:      {:4.2e}'.format( sp.sqrt((bkg + 10**2)*area)/y0 )
#    print '  signal limit:   {:4.2e}'.format(1./sp.sqrt(y0))
#    print '  total:          {:4.2e}'.format(sp.sqrt(y0 + (bkg + 10**2)*area)/y0)

#    mag = -2.5*sp.log10(y0/24.0/3600) + 20.44
#    print '  mag',mag
    

    ax1.plot(x,y,'r.',ms=1.5)

    sig = y/sp.std(y)
#    m = abs(sig) <5
    ax2.hist(sig,100, alpha =0.5,label='dispersion {:.2f}'.format(sp.std(y)))
    ax2.hist(y/z,100,facecolor='orange',alpha=0.5,label='uncertainties {:.2f}'.format(sp.median(z)))


    m = abs( y /(sp.median(abs(y))/0.67449) < 5)
    sig2 = y/sp.std(y[m])
    ax2.hist(sig2,100, alpha =0.5,label='cut dispersion {:.2f}'.format(sp.std(y[m])))

    sig3 = y/(sp.median(abs(y))/0.67449)
    ax2.hist(sig3,100, alpha =0.5,label='sigma from MAD {:.2f}'.format(sp.median(abs(y))/0.67449))

    ax2.legend(loc='upper left')


for lc in sys.argv[1:]:
    F,(ax1,ax2,ax3) = plt.subplots(3,1)
    x,y,z = sp.genfromtxt(lc, unpack=1,usecols=(0,1,2))
    x,y,z = cut_data(x,y,z)
    ax1.errorbar(x, -y, z, fmt='k.',zorder=1)

    ysmooth = median_filter(y,size=50, mode='reflect')
    yresidual = y - ysmooth
    ax1.plot(x,-ysmooth,'r',zorder=2)
    stats(x,z,yresidual, sp.mean(yresidual) ,ax2,ax3)
    
    #    plt.savefig('{}.png'.format(id1[i]))
    plt.show()
    
