#!/usr/bin/env python
import numpy as np
import scipy as sp
from scipy.interpolate import interp1d
import matplotlib
matplotlib.rcParams['font.family'] = 'serif'
#matplotlib.rcParams['font.serif'] = 'Computer Modern,Times,Bitstream Vera Serif, New Century Schoolbook, Century Schoolbook L, Utopia, ITC Bookman, Bookman, Nimbus Roman No9 L, Times New Roman, Palatino, Charter, serif'
matplotlib.rcParams['mathtext.rm'] = 'serif'
matplotlib.rcParams['mathtext.tt'] = 'monospace'
matplotlib.rcParams['mathtext.sf'] = 'serif'

import matplotlib.pyplot as plt
import sys
import os
import re
from scipy import linalg
from scipy.ndimage import median_filter
import argparse
from tess_time.cut_ffi.cut_data import get_cut_indices

def rebin(x,y,dt):
    bins = np.r_[min(x):max(x) + dt*1.001:dt]

    idxs = np.digitize(x,bins)

    out_y = np.zeros(len(bins)-1)
    out_z = np.zeros(len(bins)-1)

    for i in np.unique(idxs):
        m = np.where(idxs == i)[0]
        if len(y[m]) < 3:
            continue
        out_y[i-1] = np.mean(y[m])
        out_z[i-1] = np.std(y[m])/np.sqrt(len(y[m]))

    out_x = np.mean([bins[0:-1],bins[1::]],axis=0)
    return out_x,out_y, out_z



def remove_long_trend(x,y):
    #first, remove a 3rd order polynomail.  For SN or slowly changing
    #things, it should flatten the LCs and make the residaul
    #systematics easier to see

    p = np.polyfit(x,y,3)
    ytrend = p[0]*x**3 + p[1]*x**2 + p[2]*x + p[3]


#    return ytrend, y - ytrend
    return np.zeros(len(y)), y


def get_inputs(args):
    parser = argparse.ArgumentParser( description="feed this script a source and detrend light curve, and a region of times to fit.  shift and scale the detrend light curve, and save a source with that taken out")
    
    parser.add_argument('--source',help='Source light curve')
    parser.add_argument('--trend',help='Star with trend light curve')
    parser.add_argument('--smooth_width',default=25, type=int,
                        help='Adjusts width of median filter for smoothing trend light curve')
    parser.add_argument('--t0',help='start time to fit')
    parser.add_argument('--t1',help='end time to fit')
    parser.add_argument('--save_plot',action='store_true',help='If set, save figure with fit and subtraction')
    parser.add_argument('--show',action='store_true',help='If set, show figure with fit and subtraction')
    parser.add_argument('--clip_yscale',action='store_true',help='If set, cut the yrange to the 2--98 per cent interval of the data')

    return parser.parse_args()

def linfit(x,y,ey):
    """
    This function minimizes chi^2 for a least squares fit to a simple
    linear model.  The errors in x are assumed to be much smaller than
    the errors in y.  It automatically fills in the Fisher matrix, and
    solves the simultaneous equations.

    The function returns p, and covar.  p[0] is the zeropoint
    p[1] is the slope.


    you must take the square root to get the errors, in all cases.
    """                                                                                  
    C = np.array([np.sum(y/ey/ey),np.sum(y*x/ey/ey)])
    A = np.array([
            [np.sum(1./ey/ey), np.sum(x/ey/ey)],
            [np.sum(x/ey/ey),  np.sum(x*x/ey/ey)]
            ] )
    p     = linalg.solve(A,C)
    covar = linalg.inv(A)
    return p,covar   


def main():
    #need three things:  source, detrend, and time for fits
    args = get_inputs(sys.argv[1:])
    lc_source = args.source
    lc_detrend = args.trend
    tfit1 = float(args.t0)
    tfit2 = float(args.t1)

    data = np.genfromtxt(lc_source)
    bad_indxs = []
    print(lc_source)
    if 'detrend' not in lc_source:
        bad_indxs = get_cut_indices(data[:,0])
        data = np.delete(data,bad_indxs,axis=0)
    x,y,z = data[:,0],data[:,1], data[:,2]
    m = np.isnan(z)
    x,y,z = x[~m],y[~m],z[~m]

    x_template, y_template,z_template = np.genfromtxt(lc_detrend, 
                                                      usecols=(0, 1,2),
                                                      unpack=1)

    m = np.isnan(z_template)
    x_template,y_template = x_template[~m],y_template[~m]


    print('len x_template',len(x_template),len(x))
    m = np.in1d(x_template, x)
    x_template,y_template = x_template[m], y_template[m]
    m = np.in1d(x,x_template)
    x,y,z = x[m],y[m],z[m]
    print('len x_template',len(x_template), len(x))
    plot_y = np.copy(y)

    #    x,y,z = np.delete(x,bad_indxs), np.delete(y,bad_indxs), np.delete(z, bad_indxs)
    #if len(bad_indxs) == 0:
    #    bad_indxs = get_cut_indices(x_template)
    #x_template = np.delete(x_template, bad_indxs,axis = 0)
    #y_template2 = np.delete(y_template,bad_indxs,axis = 0)


    y_template3 = median_filter(y_template,size=args.smooth_width, mode='reflect')

    #    tfit = [1385.5,1393.6]
#    print('len x, y, y_template, y_template2,y_template3')
#    print(len(x), len(y), len(y_template), len(y_template2), len(y_template3))
    print('len x, y, y_template, y_template3')
    print(len(x), len(y), len(y_template), len(y_template3))
    #fit for scale, with nuisance shift
    mfit = (x > tfit1) & (x< tfit2)
    print(len(mfit[mfit == True]))
    p,covar = linfit(y_template3[mfit], y[mfit], np.ones(len(y[mfit])))
    residuals = y[mfit] - p[1]*y_template3[mfit] - p[0]
    print('reduced chi2: {:.2f}'.format( np.sum( residuals**2/z[mfit]**2)/np.sqrt(len(x[mfit])-2.0) ))


    #remove the trend and save
    try:
#        data[:,1] -= p[1]*y_template
        data[:,1] -= p[1]*y_template3
    except:
        interp = interp1d(x_template,y_template3,fill_value='extrapolate')
        yt = interp(data[:,0])
        data[:,1] -= p[1]*yt

    np.savetxt(args.source+'_detrended',np.c_[data])


    if args.save_plot or args.show:
        if 'zjf' in lc_source  \
           or 'tst' in lc_source or 'lrj' in lc_source:
            F,(ax1,ax2,ax3) = plt.subplots(3,1,sharex='col')
        else:
            F,(ax1,ax2,ax3) = plt.subplots(3,1,sharex='col',sharey='col')

        ax1.plot(x, -y_template,'r.',rasterized=True)
        ax1.plot(x, -y_template3,'m',rasterized=True)

        ax2.plot(x,-plot_y,'k',ms=1,rasterized=True)
        xb,yb,zb = rebin(x, -plot_y,8.0/24.0)
        m = yb == 0
        xb,yb = xb[~m],yb[~m]
        #ax2.plot(xb,yb,'go',ms=4)

        ax2.plot(x,-1*(p[0] + p[1]*y_template3),'r',rasterized=True)
        l,h = ax2.get_ylim()
        ax2.plot([tfit1,tfit1],[l,h],'k--')
        ax2.plot([tfit2,tfit2],[l,h],'k--')
        ax2.set_ylim([l,h])

        ax3.plot(data[:,0],-data[:,1],'b',ms=1,rasterized=True)
        xb,yb,zb = rebin(data[:,0],-data[:,1],8.0/24.0)
        m = yb == 0
        xb,yb = xb[~m],yb[~m]
        #ax3.plot(xb,yb,'co',ms=4)

        
        #l,h =ax1.get_ylim()
        #ax3.set_ylim([l,h])


        
        if args.clip_yscale:
            if 'zjf' in lc_source:
                p1,p2 = 0.5, 98
            elif 'ywy' in lc_source:
                p1,p2 = 10,98
            elif '20to' in lc_source:
                p1,p2 = 1,98
            elif 'ioa' in lc_source:
                p1,p2 = 1,99.5
            elif '21lsr' in lc_source:
                p1,p2 = 0.5,99.5
            elif 'tst' in lc_source:
                p1,p2 = 2,99.5
            else:
                p1,p2 = 2,98

            ylow,yhigh = np.percentile(-data[:,1],[p1,p2])
            ax3.set_ylim([ylow,yhigh])

        ax1.set_ylabel('Star Flux ($\Delta$ counts)',fontsize=16)
        ax2.set_ylabel('Fitted Flux',fontsize=16)
        ax3.set_ylabel('Detrended Flux',fontsize=16)
        ax3.set_xlabel('TJD $-$ 2457000 (days)', fontsize=16)



        sector = re.search('sector(\w*)/',os.path.abspath(lc_source))
        sector = sector.group(1)

        try:
            obj = re.search('discovery/lc_(\w*)',lc_source)
            obj = obj.group(1)
        except:
            obj = re.search('lc/lc_(\w*)',lc_source)
            obj = obj.group(1)
            

        ax1.set_title('SN {}, Sector{}'.format(obj,sector), fontsize=20)
        F.set_size_inches(8,8)
        F.subplots_adjust(hspace=0)

        if args.save_plot:

            F.savefig(args.source+'_detrended.png')
            F.savefig(args.source+'_detrended.pdf')
        if args.show:
           plt.show()


if __name__ == '__main__':
    main()
