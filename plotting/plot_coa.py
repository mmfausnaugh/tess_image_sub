#!/usr/bin/env python
import scipy as sp
import matplotlib.pyplot as plt
import sys
import os
from tess_time.cut_ffi.cut_data import cut_data



for lc in sys.argv[1:]:
    plt.figure()
    x,y = sp.genfromtxt(lc,unpack=1,usecols=(0,2))
    x,y = cut_data(x,y, sp,ones(len(x)))
    plt.errorbar(x,-y,fmt='ko',ms=3)

    try:
        suse = lc.split('/')[-4]
        plt.gca().set_title(suse + "  " + os.path.basename(lc))

        plt.savefig(suse+'_'+os.path.basename(lc)+'.png')

    except:
        plt.gca().set_title(os.path.basename(lc))


        #    plt.savefig(os.path.basename(lc)+'.png')
#    plt.show()
#    plt.close()
plt.show()
