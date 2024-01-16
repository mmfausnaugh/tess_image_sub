#!/usr/bin/env python
import numpy as np
import scipy as sp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import os
from tess_time.cut_ffi.cut_data import cut_data

dstem = sys.argv[1]
obj   = sys.argv[2]
sectors = np.r_[17:24]
infiles = []
for s in sectors:
    for ccd in [1,2,3,4]:
        infile = os.path.join('/data/tess/image_sub/sector{:02d}/cam4_ccd{}/'.format(s,ccd),
                              dstem,
                              'lc_'+obj+'_cleaned') 
        #print(infile)
        if os.path.isfile(infile):
            infiles.append(infile)

print(infiles)
x,y,z = [],[],[]
plt.figure()

for lc in infiles:
    try:
        print(lc)

        if '.png' in lc:
            print('is a png')
            continue

        if os.path.isfile(os.path.basename(lc)+'.png'):
            print('found a png')
            continue


        if 'cleaned' in lc:
            x1,y1,z1 = sp.genfromtxt(lc,unpack=1,usecols=(0,2,3))
            x = np.r_[x,x1]
            y = np.r_[y,y1]
            z = np.r_[z,z1]
            #plt.errorbar(x,y,z,fmt='ko',ms=3)
#        else:
#            x,y,z = sp.genfromtxt(lc,unpack=1,usecols=(0,1,2))
#
#            wdir = os.path.abspath(os.path.dirname(lc))
#            sector_idx = wdir.find('sector')
#            sector     = wdir[sector_idx : sector_idx+8]
#            cam_idx = wdir.find('cam')
#            cam = wdir[cam_idx : cam_idx+4]
#            ccd_idx = wdir.find('ccd')
#            ccd = wdir[ccd_idx : ccd_idx+4]
#
#
#            x,y,z = cut_data(x,y,z,sector,cam,ccd)
#            plt.errorbar(x,-y,z,fmt='ko',ms=3)
#
#        plt.savefig(lc+'.png')


    except Exception as e:
        print(e)
        continue

plt.errorbar(x,y,z,fmt='ko',ms=3)
plt.savefig('lc_'+obj+'.png')
plt.close()
#plt.show()
