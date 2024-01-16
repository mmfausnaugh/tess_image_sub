#!/usr/bin/env python
import scipy as sp
import matplotlib
#matplotlib.use('agg')
import matplotlib.pyplot as plt
import sys


for infile in sys.argv[1:]:
    print(infile)
    if '.png' in infile:
        continue
    d = sp.genfromtxt(infile)
    x,y,z,bkg = sp.genfromtxt(infile[3:],unpack=1,usecols=(0,1,2,6))

    F,((ax1,ax5),(ax2,ax6),
       (ax3,ax7),(ax4,ax8)) = plt.subplots(4,2,sharex='col')

    ax1.plot(-d[:,0],'r.')
    ax1.plot(-d[:,4],'m.')
    ax1.plot(-d[:,8],'c.')
    ax1.plot(-d[:,12],'b.')
    ax1.set_title('flux')
    ax1.plot(-y,'k.')


    ax2.plot(d[:,1],'r.')
    ax2.plot(d[:,5],'m.')
    ax2.plot(d[:,9],'c.')
    ax2.plot(d[:,13],'b.')
    ax2.set_title('bkg')
    ax2.plot(bkg,'k.')


    ax3.plot(d[:,2],'r.')
    ax3.plot(d[:,6],'m.')
    ax3.plot(d[:,10],'c.')
    ax3.plot(d[:,14],'b.')
    ax3.set_title('col')

    ax4.plot(d[:,3],'r.')
    ax4.plot(d[:,7],'m.')
    ax4.plot(d[:,11],'c.')
    ax4.plot(d[:,15],'b.')
    ax4.set_title('row')


    ax6.plot(d[:,0],d[:,1],'r.')
    ax7.plot(d[:,0],d[:,2],'r.')
    ax8.plot(d[:,0],d[:,3],'r.')

    ax6.plot(d[:,4],d[:,5],'m.')
    ax7.plot(d[:,4],d[:,6],'m.')
    ax8.plot(d[:,4],d[:,7],'m.')

    ax6.plot(d[:,8],d[:,9],'c.')
    ax7.plot(d[:,8],d[:,10],'c.')
    ax8.plot(d[:,8],d[:,11],'c.')

    ax6.plot(d[:,12],d[:,13],'b.')
    ax7.plot(d[:,12],d[:,14],'b.')
    ax8.plot(d[:,12],d[:,15],'b.')

    ax6.plot(y,bkg,'k.')
    ax7.plot(y,d[:,14],'k.')
    ax8.plot(y,d[:,15],'k.')

    #ax1.set_ylim([0.9*sp.median(d[:,12]),1.1*sp.median(d[:,12])])
    #ax2.set_ylim([0.9*sp.median(d[:,13]),1.1*sp.median(d[:,13])])
    ax3.set_ylim([sp.median(d[:,14]) - 1.0 ,sp.median(d[:,14]) + 1.0])
    ax4.set_ylim([sp.median(d[:,15]) - 1.0 ,sp.median(d[:,15]) + 1.0])
    ax7.set_ylim([sp.median(d[:,14]) - 1.0 ,sp.median(d[:,14]) + 1.0])
    ax8.set_ylim([sp.median(d[:,15]) - 1.0 ,sp.median(d[:,15]) + 1.0])


    F.set_size_inches(16,16)
    #    F.savefig(infile + '.png')
    F,(ax1) = plt.subplots(1,1)
    ax1.plot(-d[:,0],'r.')
    ax1.plot(-d[:,4],'m.')
    ax1.plot(-d[:,8],'c.')
    ax1.plot(-d[:,12],'b.')
    ax1.set_title('flux')
    ax1.plot(-y,'k.')

    plt.show()
