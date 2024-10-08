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
from scipy import optimize,linalg
from scipy.stats import kstest 


#compare flatness (constant stars)
def linfit(x,y,ey): 
    C = sp.array([sp.sum(y/ey/ey),sp.sum(y*x/ey/ey)])
    A = sp.array([
            [sp.sum(1./ey/ey), sp.sum(x/ey/ey)],
            [sp.sum(x/ey/ey),  sp.sum(x*x/ey/ey)]
    ] )
    p     = linalg.solve(A,C)
    covar = linalg.inv(A)
    return p,covar

def med_filter(y):
    med = sp.zeros(len(y))
    for i in range(len(y)):
        med[i] = sp.median(y[ max(i-10,0): min(i+10,len(y)-1)])
    return y - med,med 

def get_flatness(t,y):
    p,covar = linfit(t-t.mean(),y-y.mean(),sp.ones(len(y)))
    slope = p[1]
    eslope = sp.sqrt(covar[1,1])
    return slope,eslope

#compare connection between orbits
def get_orbit_slope(t,y):
    #there should be few to no gaps larger than 4 hours (usual LAHO is
    #~8 hr or more
    delta_t = sp.diff(t)
    idx = sp.where(delta_t > 4.0/24.0)[0]
    assert len(idx) == 1
    idx = idx[0]

    #fit 0.5 days on either side == 24 FFIs    
    t_fit = sp.r_[ t[idx - 24:idx], t[idx+1: idx +25 ] ]
    y_fit = sp.r_[ y[idx - 24:idx], y[idx+1: idx +25 ] ]
    p,covar = linfit(t_fit - t_fit.mean(),y_fit - y_fit.mean(),sp.ones(len(y_fit)))
    slope = p[1]
    eslope = sp.sqrt(covar[1,1])
    return slope,eslope

#compare to white noise---use KS test statistic and probability
def compare_noise(y):
    res = y - sp.median(y)
    sigma = sp.median(abs(res))/0.67449
    res_norm = res/sigma
    ks,p = kstest(res_norm,'norm')
    return sigma,ks,p


def do_comps(t,y):
    y_flat,y_med = med_filter(y)
    s1,es1 = get_flatness(t,y_flat)
    s2,es2 = get_orbit_slope(t,y_flat)
    sigma,ks,p   = compare_noise(y_flat)

    return [s1,es1,s2,es2,sigma,ks,p]

def compare_lc(x1,y1,x2,y2):
    m = sp.ones(len(x1),dtype=bool)
    for ii,epoch in enumerate(x1):
        if any(sp.isclose(x2,epoch,atol=1.e-5)):
            m[ii] = False
    idx = sp.where(m)[0]
    xuse1,yuse1 = sp.delete(x1,idx),sp.delete(y1,idx)

    m = sp.ones(len(x2),dtype=bool)
    for ii,epoch in enumerate(x2):
        if any(sp.isclose(xuse1,epoch,atol=1.e-5)):
            m[ii]=False
    idx = sp.where(m)[0]
    xuse2,yuse2 = sp.delete(x2,idx),sp.delete(y2,idx)

    #print('pdc:',len(yuse2),len(y2),'isis:',len(yuse1),len(y1))
    #print(sp.c_[xuse2[0:5],xuse1[0:5]])
    p,covar = linfit(yuse2,yuse1,sp.ones(len(yuse2)))

    res = yuse1 - p[0] - p[1]*yuse2
    #plt.figure()
    #plt.plot(x2,p[0] + p[1]*y2,'g.')
    #plt.plot(x1,y1,'k.')
    #plt.show()
    return sp.sqrt(sp.mean(res**2)),p[0],p[1]


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


#compare SAP, PDCSAP, PSF, and circle aps
sap_out = []
pdc_out = []
psf_out = []
circ6_out = []
circ8_out = []
circ10_out = []

for infile in sys.argv[1:]:
    print(infile)
    if '.png' in infile:
        continue
    d = sp.genfromtxt(infile)
    try:
        x_orig,y,z,bkg = sp.genfromtxt(infile[3:],unpack=1,usecols=(0,1,2,6))
    except:
        continue
    if len(d) == 0:
        continue


    tic = infile.split('_')[-1]
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
    bt -= 0.010416666666666666
    
    x,d1,bkg1 = cut_data(x_orig,d[:,0], d[:,1])
    x,d2,bkg2 = cut_data(x_orig,d[:,4], d[:,5])
    x,d3,bkg3 = cut_data(x_orig,d[:,8], d[:,9])
    x,d4,bkg4 = cut_data(x_orig,d[:,12],d[:,13])
    x,d5,bkg5 = cut_data(x_orig,d[:,16],d[:,17])
    x,d6,bkg6 = cut_data(x_orig,d[:,18],d[:,19])
    x,d7,bkg7 = cut_data(x_orig,d[:,20],d[:,21])

    x,y,bkg = cut_data(x_orig,y,bkg)


    sap_out.append(sp.r_[fhandle[0].header['TESSMAG'],do_comps(bt,sap)])
    pdc_out.append(sp.r_[fhandle[0].header['TESSMAG'],do_comps(bt,pdc_sap)])
    psf_out.append(sp.r_[fhandle[0].header['TESSMAG'],do_comps(x,y),compare_lc(x,y,bt,pdc_sap)])
    circ6_out.append(sp.r_[fhandle[0].header['TESSMAG'],do_comps(x,d5),compare_lc(x,d5,bt,pdc_sap)])
    circ8_out.append(sp.r_[fhandle[0].header['TESSMAG'],do_comps(x,d6),compare_lc(x,d6,bt,pdc_sap)])
    circ10_out.append(sp.r_[fhandle[0].header['TESSMAG'],do_comps(x,d7),compare_lc(x,d7,bt,pdc_sap)])

print(sp.array(sap_out))
sp.savetxt('sap_stats.txt',sp.array(sap_out))
sp.savetxt('pdc_stats.txt',sp.array(pdc_out))
sp.savetxt('psf_stats.txt',sp.array(psf_out))
sp.savetxt('circ6_stats.txt', sp.array(circ6_out))
sp.savetxt('circ8_stats.txt', sp.array(circ8_out))
sp.savetxt('circ10_stats.txt',sp.array(circ10_out))
