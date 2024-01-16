#!/usr/bin/env python
import scipy as sp
import matplotlib
#matplotlib.use('agg')
import matplotlib.pyplot as plt
import sys
from tess_time.cut_ffi.cut_data import cut_data                                           


for infile in sys.argv[1:]:
    print(infile)
    if '.png' in infile:
        continue
    d = sp.genfromtxt(infile)
    x_orig,y,z,bkg = sp.genfromtxt(infile[3:],unpack=1,usecols=(0,1,2,6))

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

    ax1.legend()
    F.set_size_inches(16,16)

    F2,(ax2) = plt.subplots(1,1)
    scale = max(bkg1) - min(bkg1)
#    scale = 0
    ax2.plot(x,bkg1 + scale,'r.',label='5 box')
    ax2.plot(x,bkg2 + 2*scale,'.',color='purple',label='7 box')
    ax2.plot(x,bkg3 + 3*scale,'.',color='orange',label='9 box')
    ax2.plot(x,bkg4 + 4*scale,'.',color='brown',label= '11 box')
    ax2.plot(x,bkg5 + 5*scale,'b.',label= '6 circ')
    ax2.plot(x,bkg6 + 6*scale,'c.',label= '8 circ')
    ax2.plot(x,bkg7 + 7*scale,'m.',label= '10 circ')

    ax2.set_title('flux')
    ax2.plot(x,bkg,'k.',label='ISIS')

    ax2.legend()
    F2.set_size_inches(16,16)
    plt.show()
