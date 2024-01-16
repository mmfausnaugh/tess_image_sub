#!/usr/bin/env python
import scipy as sp
import matplotlib
#matplotlib.use('agg')
import matplotlib.pyplot as plt
import sys
from tess_time.cut_ffi.cut_data import cut_data                                         
from astropy.io import fits 
import os
import glob

def rebin(t, x, delta_t):    
    bins = sp.r_[min(t): max(t) + delta_t + 0.1: delta_t]
    idxs = sp.digitize(t, bins)
    out_x = sp.zeros(len(bins) - 1)
    for i in sp.unique(idxs):
        m = sp.where(idxs == i)[0]
        out_x[i -1] = sp.mean(x[m])
    out_t = sp.mean([bins[0:-1],bins[1::]],axis=0) 
    return out_t, out_x

dstem = '/pdo/spoc_products/'
sector = os.getcwd()
sector = sector.split('/')[-3]
sector = sector[-1]
dstem = dstem + 's'+sector+'_target/light-curve/'

for infile in sys.argv[1:]:
    print(infile)
    if '.png' in infile:
        continue
    d = sp.genfromtxt(infile)
    if len(d) == 0:
        continue
    x_orig,y,z,bkg = sp.genfromtxt(infile[3:],unpack=1,usecols=(0,1,2,6))


    tic = infile[7:]
    lcfile = glob.glob(dstem + '*{}*'.format(tic))
    print dstem + '*{}*'.format(tic)
    print lcfile
    assert len(lcfile) == 1    
    fhandle = fits.open(lcfile[0])
    print fhandle[0].header['TESSMAG']
    quality = fhandle[1].data['QUALITY']
    m = quality > 0
    t = fhandle[1].data['TIME'][~m]
    sap = fhandle[1].data['SAP_FLUX'][~m]*720
    pdc_sap = fhandle[1].data['PDCSAP_FLUX'][~m]*1440
    bkg_sap = fhandle[1].data['SAP_BKG'][~m]*1440

    bt, sap = rebin(t,sap,0.5/24.0)
    m = sap == 0
    bt,sap = bt[~m],sap[~m]
    bt, pdc_sap = rebin(t,pdc_sap,0.5/24.0)
    bt,pdc_sap = bt[~m],pdc_sap[~m]
    bt, bkg_sap = rebin(t,bkg_sap,0.5/24.0)
    bt,bkg_sap = bt[~m],bkg_sap[~m]

    x,y,bkg = cut_data(x_orig,y,bkg)
    
    x,d1,bkg1 = cut_data(x_orig,d[:,0], d[:,1])
    x,d2,bkg2 = cut_data(x_orig,d[:,4], d[:,5])
    x,d3,bkg3 = cut_data(x_orig,d[:,8], d[:,9])
    x,d4,bkg4 = cut_data(x_orig,d[:,12],d[:,13])
    x,d5,bkg5 = cut_data(x_orig,d[:,16],d[:,17])
    x,d6,bkg6 = cut_data(x_orig,d[:,18],d[:,19])
    x,d7,bkg7 = cut_data(x_orig,d[:,20],d[:,21])


    scale = max(y) - min(y)
    #scale  = 0
    F,(ax1) = plt.subplots(1,1)
    ax1.plot(x,-d1 + scale,'r.',label='5 box')
    ax1.plot(x,-d2 + 2*scale,'.',color='purple',label='7 box')
    ax1.plot(x,-d3 + 3*scale,'.',color='orange',label='9 box')
    ax1.plot(x,-d4 + 4*scale,'.',color='brown',label= '11 box')
    ax1.plot(x,-d5 + 5*scale,'b.',label= '6 circ')
    ax1.plot(x,-d6 + 6*scale,'c.',label= '8 circ')
    ax1.plot(x,-d7 + 7*scale,'m.',label= '10 circ')

    ax1.set_title('flux')
    ax1.plot(x,-y,'k.',label='ISIS')

#    ax1.plot(bt,sap - sap.mean() + 8*scale,'ko',mfc='w')
#    ax1.plot(bt,pdc_sap - pdc_sap.mean() + 9*scale,'go',mfc='w')
    ax1.plot(bt,sap - sap.mean() + 8*scale,'k.')
    ax1.plot(bt,pdc_sap - pdc_sap.mean() + 9*scale,'g.')

    ax1.legend()
    F.set_size_inches(16,16)

###    F2,(ax2) = plt.subplots(1,1)
###    scale = max(bkg1) - min(bkg1)
####    scale = 0
###    ax2.plot(x,bkg1 + scale,'r.',label='5 box')
###    ax2.plot(x,bkg2 + 2*scale,'.',color='purple',label='7 box')
###    ax2.plot(x,bkg3 + 3*scale,'.',color='orange',label='9 box')
###    ax2.plot(x,bkg4 + 4*scale,'.',color='brown',label= '11 box')
###    ax2.plot(x,bkg5 + 5*scale,'b.',label= '6 circ')
###    ax2.plot(x,bkg6 + 6*scale,'c.',label= '8 circ')
###    ax2.plot(x,bkg7 + 7*scale,'m.',label= '10 circ')
###
###    ax2.set_title('bkg flux')
###    ax2.plot(x,bkg,'k.',label='ISIS')
###    ax2.plot(bt,bkg_sap - bkg_sap.mean(),'ko',mfc='w')
###
###    ax2.legend()
###    F2.set_size_inches(16,16)
    plt.show()
