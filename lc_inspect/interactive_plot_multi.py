#!/usr/bin/env python 
import numpy as np
from astropy.io import fits

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt

import os
import sys

import argparse

from tess_time.cut_ffi.cut_data import cut_data


def find_images(times, image_files, time_match, dstem):
    dt = abs(times - time_match)
    idx_match = np.where(dt == min(dt) )[0][0]

    ##print(times[idx_match],time_match)
    ##print(idx_match)
    ##print(np.c_[times[idx_match -1 : idx_match + 2],
    ##            image_files[idx_match -1 : idx_match +2 ]])

    image_return = [ dstem + '/conv_' + im for im in image_files[idx_match - 1: idx_match +2 ] ]
    return image_return 


#plt.ion()
F = plt.figure()

gs1 = gridspec.GridSpec(4,3)

#light curve
ax1 = F.add_subplot( gs1[0:3] )
#ref
ax2 = F.add_subplot( gs1[2,0] )
#rms
ax3 = F.add_subplot( gs1[2,1] )

#before, during, and after mouse click
ax4 = F.add_subplot( gs1[3,0] )
ax5 = F.add_subplot( gs1[3,1] )
ax6 = F.add_subplot( gs1[3,2] )


#global view of the difference image, to look for weird background
ax7 = F.add_subplot( gs1[2,2] )

#bkg plot, and zoom in of lc
ax8 = F.add_subplot( gs1[1,0] )
ax9 = F.add_subplot( gs1[1,1:] )

print(os.getcwd())
infile = sys.argv[1]

wdir = os.path.abspath(os.path.dirname(infile))
#sector_idx = wdir.find('sector')
#sector     = wdir[sector_idx : sector_idx+8]
#cam_idx = wdir.find('cam')
#cam = wdir[cam_idx : cam_idx+4]
#ccd_idx = wdir.find('ccd')
#ccd = wdir[ccd_idx : ccd_idx+4]

#dstem = os.path.join('/data/tess/image_sub/',
#                     sector,cam + '_' + ccd)
dstem = os.path.join(os.path.abspath(
                     os.path.dirname(infile)),'..')

ref_file =  os.path.join(dstem, 'ref.fits')
rms_file =  os.path.join(dstem, 'rms.fits')
date_file = os.path.join(dstem, 'dates')
phot_file = 'phot.data'

if 'cleaned' in infile:
    x,y,z,bkg  = np.genfromtxt(infile,unpack=1,usecols=(1,2,3,4))
else:
    x,y,z,bkg = np.genfromtxt(infile,unpack=1,usecols=(0,1,2, 6))
    y *= -1
    bkg *= 1

    try:
        x2,y,z = cut_data(x,y,z,sector,cam,ccd)
        x,bkg,_ = cut_data(x,bkg,bkg,sector,cam,ccd)
    except:
        pass


ax1.errorbar(x,y,z,fmt='k.')
ax9.plot(x,bkg,'m.')
ax9.set_title('Background')
#can add binning here


#get coords, plot up ref and rms image
phot_data = np.genfromtxt(phot_file, dtype=str)
if len(np.shape(phot_data)) == 1:
    phot_data = np.array([phot_data])
print(phot_data,type(phot_data),len(np.shape(phot_data )) )
names = np.array([lc.replace('lc/','') for lc in phot_data[:,4] ])
print(phot_file)
print(names)
lookup_file = np.in1d(names, infile.replace('_cleaned','') )
col,row, col_px,row_px = phot_data[lookup_file][0][ [0,1,2,3] ]
print(col,col_px)
col = float(col)
row = float(row)
col_px = int(col_px)
row_px = int(row_px)
print(col,col_px, col-col_px + 5)

ref_image = fits.getdata(ref_file)
try:
    rms_image = fits.getdata(rms_file)
except IOError:
    rms_image = np.zeros((2048,2048))

col_idx = slice( col_px - 5, col_px + 6,1)
row_idx = slice( row_px - 5, row_px + 6,1)


vl,vh = np.percentile( np.ravel(ref_image[row_idx, col_idx]),[10,90])
ax2.imshow(ref_image[row_idx, col_idx],origin='lower',
           vmin = vl, vmax = vh )
ax2.plot(col - col_px + 5,
         row - row_px + 5,'bo')
ax2.set_title('ref')


vl,vh = np.percentile( np.ravel(rms_image[row_idx, col_idx]),[10,90])
ax3.imshow(rms_image[row_idx, col_idx],origin='lower',
           vmin = vl, vmax = vh )
ax3.plot(col - col_px + 5,
         row - row_px + 5,'bo')
ax3.set_title('rms')


#get times and image list
image_files = np.genfromtxt(date_file,usecols=(0),dtype=str)
times       = np.genfromtxt(date_file,usecols=(1))


# find match from mouse click
def onclick(event):
    ax1.cla()
    ax4.cla()
    ax5.cla()
    ax6.cla()
    ax7.cla()
    ax8.cla()
    ax9.cla()


    time_match = event.xdata
    print(event.xdata,event.ydata)
    print(time_match)
    
    ax1.errorbar(x,y,z,fmt='k.')
    l,h = ax1.get_ylim()
    ax1.plot([time_match, time_match],[l,h],'r--')
    ax1.set_ylim([l,h])

    ax9.plot(x,bkg,'m.')
    l,h = ax9.get_ylim()
    ax9.plot([time_match, time_match],[l,h],'r--')
    ax9.set_ylim([l,h])


    tmask = (x > time_match - 0.5/24.0*5) & (x < time_match + 0.5/24.0*6)
    ax8.errorbar(x[tmask],y[tmask],z[tmask],fmt='k.')
    l,h = ax8.get_ylim()
    ax8.plot([time_match, time_match],[l,h],'r--')
    ax8.set_ylim([l,h])
    

    images_to_plot = find_images(times, image_files, time_match, dstem)
    axes = [ax4,ax5,ax6]

    vl,vh = np.percentile( np.ravel(fits.getdata(images_to_plot[0])[row_idx, col_idx]),[10,90])

    for ii,im in enumerate(images_to_plot):
        fin = im.split('_')[-2]
        d = fits.getdata(im)
        axes[ii].imshow(d[row_idx, col_idx],origin='lower',
                        vmin = vl, vmax = vh)
        axes[ii].plot(col - col_px + 5, row - row_px + 5,'bo')
        axes[ii].set_title('FIN = {}'.format(fin))
        
        if ii == 1:
            print(im)
            print(col_px, row_px)
            col_idx2 = slice( col_px - 50, col_px + 51,1)
            row_idx2 = slice( row_px - 50, row_px + 51,1)
            ax7.imshow(d[row_idx2, col_idx2], origin='lower',
                       vmin = vl, vmax = vh)



    plt.draw()
    #F.canvas.mpl_disconnect(cid)
F.tight_layout()
F.set_size_inches(12,12)

cid = F.canvas.mpl_connect('button_press_event',onclick)

plt.show()
