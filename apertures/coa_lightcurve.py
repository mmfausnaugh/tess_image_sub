#!/usr/bin/env python
import scipy as sp
from astropy.io import fits
import argparse
import sys
import os
from scipy.stats import sigmaclip, mode

import matplotlib.pyplot as plt

def photometry(im, row,cols,ref_row,ref_col):
    #sum the counts in the aperture
    sum_cts = 0.0
    for z in zip (row,cols):
        sum_cts += im[(z[0],z[1])]

    #calcualte the background
#    bkg = background(im, ref_row, ref_col, verbose=True)
    bkg = background(im, ref_row, ref_col)

    return sum_cts - len(row)*bkg, bkg, len(row)*bkg

def background(im, ref_row, ref_col, verbose=False):
    bkg_image = sp.ravel(im[ref_row-15:ref_row+16, ref_col-15:ref_col+16])
    if verbose:
        print '{:>10s} {:>10s} {:>10s}'.format('mean','median','mode')
        print '{:10.2f} {:>10.2f} {:>10.2f}'.format(sp.mean(bkg_image),
                                                    sp.median(bkg_image),
                                                    mode(bkg_image)[0][0],
                                                    2.5*sp.median(bkg_image) - 1.5*sp.mean(bkg_image))

#    bins = sp.r_[bkg_image.min(): bkg_image.max():500j]
#    plt.hist(bkg_image,bins,alpha=0.3)

    flag = True
    while flag:
        if verbose:
            print 'sigclipping...'
        bkg_image2,low,high = sigmaclip(bkg_image,low=10.0,high=2.0) 
        if len(bkg_image2) == len(bkg_image):
            flag = False
        else:
            bkg_image = bkg_image2
        
            #    plt.hist(bkg_image2,bins,alpha=0.3)
            #    print 'low:',low,'high:',high, 'length:',len(bkg_image2)
    if verbose:
        print '{:>10.2f} {:>10.2f} {:>10.2f} {:>10.2f}'.format(sp.mean(bkg_image2),
                                                               sp.median(bkg_image2),
                                                               mode(bkg_image2)[0][0],
                                                               2.5*sp.median(bkg_image2) - 1.5*sp.mean(bkg_image2) )
        #    plt.show()

    #this equation comes from the source extractor reference manual,
    #which is an estimate of the mode for a crowded region of the sky
    return 2.5*sp.median(bkg_image2) - 1.5*sp.mean(bkg_image2)
    

def get_inputs(args):
    parser = argparse.ArgumentParser( description="Uses COA results to sum counts in optimal aperture and subtract the background")
    parser.add_argument("images", nargs='+',help="Image for photometry")
    parser.add_argument("--photfile", help="COA results file")
    parser.add_argument("--outdir", default='./', help="location for output file")
    return parser.parse_args()


def main():

    args = get_inputs(sys.argv[1:])
    catID, target, ra, dec, mag, flux_frac, crowding, oa_rows, oa_cols, ref_row, ref_col = sp.genfromtxt(args.photfile,unpack=1,dtype=str)

    try:
        len(ref_row.astype(int))
    except:
        catID = sp.array([catID])
        target = sp.array([target])
        ra = sp.array([ra])
        dec = sp.array([dec])
        mag = sp.array([mag])
        flux_frac = sp.array([flux_frac])
        crowding = sp.array([crowding])
        oa_rows = sp.array([oa_rows])
        oa_cols = sp.array([oa_cols])
        ref_row = sp.array([ref_row])
        ref_col = sp.array([ref_col])

    catID = catID.astype(int)
    ra,dec,mag = ra.astype(float), dec.astype(float), mag.astype(float)
    flux_frac, crowding = flux_frac.astype(float), crowding.astype(float)
    ref_row, ref_col = ref_row.astype(int), ref_col.astype(int)


    #format string for writting
    fmt='{:15.2f} {:15.2f} {:15.2f} {:15.2f}\n'

    #open all the LC files
    fhandles = []
    oa_rows_use = []
    oa_cols_use = []

    for ii in range(len(target)):
        #this file can be at the sector level, since it is filtered on name
        fhandles.append( 
            open(os.path.join(args.outdir,'coa_lc_{}'.format(target[ii])),'w')
        )
        #one day, add the errors...
#        fhandles[ii].write('#' + '{:>15s} {:>15s} {:>15s} {:>15s}\n'.format('final_cts','cts','bkg','median_bkg'))

        #subtract 1 because python indexes at 0
        oa_rows_use.append(sp.array([  int(s) -1  for s in oa_rows[ii].split(',')[0:-1] ]))
        oa_cols_use.append(sp.array([  int(s) -1  for s in oa_cols[ii].split(',')[0:-1] ]))


    for imagefile in args.images:
        print(imagefile)
        image = fits.open(imagefile)[0].data        
        for ii in range(len(target)):
        
            cts, bkg_median, bkg = photometry(image, 
                                              oa_rows_use[ii],
                                              oa_cols_use[ii],
                                              ref_row[ii],
                                              ref_col[ii])

            corrected_cts = (cts*crowding[ii])/flux_frac[ii]
            fhandles[ii].write(fmt.format(corrected_cts, cts, 
                                          bkg, bkg_median))
    
    for ii in range(len(fhandles)):
        fhandles[ii].close()


if __name__ == '__main__':
    main()
