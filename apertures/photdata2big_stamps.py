#!/usr/bin/env python
import numpy as np
from astropy.io import fits
import argparse
import sys
import os
from scipy.stats import sigmaclip, mode

import re

import matplotlib.pyplot as plt

def photometry(im, row,cols,ref_row,ref_col, save_stamp=False):
    #sum the counts in the aperture
    sum_cts = 0.0
    for z in zip (row,cols):
        sum_cts += im[(z[0],z[1])]

    #calcualte the background
#    bkg = background(im, ref_row, ref_col, verbose=True)
    bkg = background(im, ref_row, ref_col, save_stamp=save_stamp)

    return sum_cts - len(row)*bkg, bkg, len(row)*bkg

def make_stamp(im, ref_row, ref_col,obj,image_name):
    print(ref_row,ref_col)
    fits.writeto('stamp{}_{}_row{}_col{}.fits'.format(
        os.path.splitext(image_name)[0],
        obj, ref_row,ref_col),
                 im[ref_row-150:ref_row+151, ref_col-150:ref_col+151])

def background(im, ref_row, ref_col, verbose=False, save_stamp=False):

    if save_stamp:
        fits.writeto('stamp_row{}_col{}.fits'.format(ref_row,ref_col),
                     im[ref_row-35:ref_row+36, ref_col-35:ref_col+36])
    bkg_image = np.ravel(im[ref_row-15:ref_row+16, ref_col-15:ref_col+16])
    if verbose:
        print('{:>10s} {:>10s} {:>10s}'.format('mean','median','mode'))
        print('{:10.2f} {:>10.2f} {:>10.2f}'.format(np.mean(bkg_image),
                                                    np.median(bkg_image),
                                                    mode(bkg_image)[0][0],
                                                    2.5*np.median(bkg_image) - 1.5*np.mean(bkg_image)))

#    bins = np.r_[bkg_image.min(): bkg_image.max():500j]
#    plt.hist(bkg_image,bins,alpha=0.3)

    flag = True
    while flag:
        if verbose:
            print('sigclipping...')
        bkg_image2,low,high = sigmaclip(bkg_image,low=10.0,high=2.0) 
        if len(bkg_image2) == len(bkg_image):
            flag = False
        else:
            bkg_image = bkg_image2
        
            #    plt.hist(bkg_image2,bins,alpha=0.3)
            #    print 'low:',low,'high:',high, 'length:',len(bkg_image2)
    if verbose:
        print('{:>10.2f} {:>10.2f} {:>10.2f} {:>10.2f}'.format(np.mean(bkg_image2),
                                                               np.median(bkg_image2),
                                                               mode(bkg_image2)[0][0],
                                                               2.5*np.median(bkg_image2) - 1.5*np.mean(bkg_image2) ))
        #    plt.show()

    #this equation comes from the source extractor reference manual,
    #which is an estimate of the mode for a crowded region of the sky
    return 2.5*np.median(bkg_image2) - 1.5*np.mean(bkg_image2)
    

def get_inputs(args):
    parser = argparse.ArgumentParser( description="Use photdata file to make cutouts around objects")
    parser.add_argument("--images", nargs="*",help="Image for stamps")
    parser.add_argument("--photfile",help="phot.data file")
    parser.add_argument("--outdir", default='./', help="location for output file")
    return parser.parse_args()


def main():

    args = get_inputs(sys.argv[1:])

    #    images = fits.getdata(args.images)
    print(args.photfile)
    ref_col,ref_row = np.genfromtxt(args.photfile,unpack=1,usecols=(2,3),dtype=int)
    objects = np.genfromtxt(args.photfile,usecols=(4),dtype=str)
    objs = np.array([re.search('lc/lc_(\w*)',obj).group(1) for obj in objects ])
    try:
        len(ref_row.astype(int))
    except:
        ref_row = np.array([ref_row]).astype(int)
        ref_col = np.array([ref_col]).astype(int)

    for image_name in args.images:

        image = fits.getdata(image_name)
        for ii in range(len(ref_row)):
            make_stamp(image, ref_row[ii], ref_col[ii], objs[ii], image_name)


if __name__ == '__main__':
    main()
