#!/usr/bin/env python
import numpy as np
import scipy as sp
from astropy.io import fits
import photutils as phot
import argparse
import sys
import os

from apertures.pixelstamp import PixelStamp


#this command at the shell can compile a bunch LCs into one file
#for i in $(ls); do paste <(echo "$i") <(tail -n 1 $i); done

def get_inputs(args):
    parser = argparse.ArgumentParser(
        description="program to try a couple box apertures and calculate centroids")
    parser.add_argument('--photfile', help='Input file of sources and coords, just two column col, row')
    parser.add_argument('--infiles', nargs="*", help="list of input files for photometr, append to lc file in this order")
        #could add aperture options, etc.
        

    return parser.parse_args()

def get_photdata(photfile):

    cols,rows = np.genfromtxt(photfile,unpack=1)
    names = []
    for ii in range(len(cols)):
        names.append('lc/lc_{:06d}.{:.0f}.{:.0f}'.format(ii,cols[ii],rows[ii]))


    return [sp.array(cols),
            sp.array(rows),
            names]

def make_regions():
    bkgs = sp.zeros((6,15,15),dtype=bool)
    bkgs[:,0:2,:] = 1
    bkgs[:,:,0:2] = 1
    bkgs[:,13:,:] = 1
    bkgs[:,:,13:] = 1

    aps = sp.zeros((6,15,15),dtype=bool)
    #defaults to 5x5, 7x7, 9x9, and 11x11
    aps[0,7,7] = 1
    aps[0,6:9,6:9] = 1
    aps[0,5:10,5:10] = 1
    aps[1,4:11,4:11] = 1
    aps[2,3:12,3:12] = 1
    aps[3,2:13,2:13] = 1
    return aps,bkgs


def do_phot(infile, photdata):
    fmt = '{:15.6f} {:10.6f} {:10.4f} {:10.4f}'
    with fits.open(infile) as fhandle:
        im = fhandle[0].data
        
        #make a bunch of apertures and background regions
        aps,bkgs = make_regions()


        for ii in range(sp.shape(photdata)[1]):            
            col_center, row_center, fname = photdata[0][ii], photdata[1][ii], photdata[2][ii]
            if col_center < 54 or col_center > 2089 or row_center < 10 or row_center > 2038 :
                continue
            with open(fname,'a') as fout_phot:
                trunc_col_center = sp.around(col_center)
                trunc_row_center = sp.around(row_center)
                cmin = int(trunc_col_center - 7)
                cmax = int(trunc_col_center + 7)
                rmin = int(trunc_row_center - 7)
                rmax = int(trunc_row_center + 7)

                p = PixelStamp(im[rmin:rmax + 1,
                                  cmin:cmax + 1])
                for ap_use,bkg_use in zip(aps,bkgs):
                    fout,bkg,col,row = p.compute_phot(ap_use, bkg_use)
                    col += col_center
                    row += row_center
                    fout_phot.write( fmt.format(fout,bkg,col,row) )
                f1,bkg1,f2,bkg2 = p.small_circle_phot(col_center - cmin, row_center-rmin)
                fout_phot.write('{:15.6f} {:10.6f} {:15.6f} {:10.6f}'.format(
                    f1,bkg1,f2,bkg2) )
                f1,bkg1,f2,bkg2,f3,bkg3 = p.circle_phot(col_center - cmin, row_center-rmin)
                fout_phot.write('{:15.6f} {:10.6f} {:15.6f} {:10.6f} '\
                                '{:15.6f} {:10.6f}\n'.format(f1,bkg1,f2,bkg2,f3,bkg3) )


def main():
    
    args = get_inputs(sys.argv[1:])
    photdata = get_photdata(args.photfile)

    for fname in photdata[2]:
        with open(fname,'w') as fout_phot:
            out_header = '{:>15s} {:>10s} {:>10s} {:>10s} '\
                         '{:>15s} {:>10s} {:>10s} {:>10s} '\
                         '{:>15s} {:>10s} {:>10s} {:>10s} '\
                         '{:>15s} {:>10s} {:>10s} {:>10s} '\
                         '{:>15s} {:>10s} {:>10s} {:>10s} '\
                         '{:>15s} {:>10s} {:>10s} {:>10s} '\
                         '{:>15s} {:>10s} '\
                         '{:>15s} {:>10s} '\
                         '{:>15s} {:>10s} '\
                         '{:>15s} {:>10s} '\
                         '{:>15s} {:>10s} '

            

            fout_phot.write(out_header.format('f_1x1','bkg_1x1','col_1x1','row_1x1',
                                              'f_3x3','bkg_3x3','col_3x3','row_3x3',
                                              'f_5x5','bkg_5x5','col_5x5','row_5x5',
                                              'f_7x7','bkg_7x7','col_7x7','row_7x7',
                                              'f_9x9','bkg_9x9','col_9x9','row_9x9',
                                              'f_9x9','bkg_11x11','col_11x11','row_11x11',
                                              'f_1rad','bkg_1rad',
                                              'f_2rad','bkg_2rad',
                                              'f_3rad','bkg_3rad',
                                              'f_4rad','bkg_4rad',
                                              'f_5rad','bkg_5rad'
                                              ))
            fout_phot.write('\n')

    for infile in args.infiles:
        do_phot(infile, photdata)
    
if __name__ == '__main__':
    main()
