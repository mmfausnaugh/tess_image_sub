#!/usr/bin/env python
<<<<<<< HEAD
import numpy as np
=======
>>>>>>> 7a22a11ef1034de2480b1598802c4de028eddf56
import scipy as sp
from astropy.io import fits
import photutils as phot
import argparse
import sys
import os

from apertures.pixelstamp import PixelStamp


def get_inputs(args):
    parser = argparse.ArgumentParser(
        description="program to try a couple box apertures and calculate centroids")
    parser.add_argument('--photfile', help='Input file of sources and coords, matches phot.data for ISIS')
    parser.add_argument('--infiles', nargs="*", help="list of input files for photometr, append to lc file in this order")
        #could add aperture options, etc.
        

    return parser.parse_args()

def get_photdata(photfile):
<<<<<<< HEAD
    names = np.genfromtxt(photfile,usecols=(4),dtype=str)
    col,row = np.genfromtxt(photfile,unpack=1,usecols=(0,1))
    with open(photfile,'r') as fin:
        if len(fin.readlines()) > 1:
            pass
        else:
            names = np.array([names])
            col = np.array([col])
            row = np.array([row])


    print(col,row,names, type(names) )
=======
    col,row = sp.genfromtxt(photfile,unpack=1,usecols=(0,1))
    names = sp.genfromtxt(photfile,usecols=(4),dtype=str)
>>>>>>> 7a22a11ef1034de2480b1598802c4de028eddf56
    name_out = []
    for name in names:
        s = name.split('/')
        name_out.append(  os.path.join(s[0], 'ap_small_'+s[1])  )
    return [col,row,name_out]

def make_regions():
<<<<<<< HEAD
    bkgs = np.zeros((2,15,15),dtype=bool)
=======
    bkgs = sp.zeros((2,15,15),dtype=bool)
>>>>>>> 7a22a11ef1034de2480b1598802c4de028eddf56
    bkgs[:,0:2,:] = 1
    bkgs[:,:,0:2] = 1
    bkgs[:,13:,:] = 1
    bkgs[:,:,13:] = 1

<<<<<<< HEAD
    aps = np.zeros((2,15,15),dtype=bool)
=======
    aps = sp.zeros((2,15,15),dtype=bool)
>>>>>>> 7a22a11ef1034de2480b1598802c4de028eddf56
    #defaults to 1x1 and 3x3, which is everything not in lc_ap_phot.py
    aps[0,7,7] = 1
    aps[1,6:9,6:9] = 1
    return aps,bkgs


def do_phot(infile, photdata):
    fmt = '{:15.2f} {:10.2f} {:10.4f} {:10.4f}'
    #make a bunch of apertures and background regions        
    aps,bkgs = make_regions()

    with fits.open(infile) as fhandle:
        im = fhandle[0].data
        


<<<<<<< HEAD
        for ii in range(np.shape(photdata)[1]):            
=======
        for ii in range(sp.shape(photdata)[1]):            
>>>>>>> 7a22a11ef1034de2480b1598802c4de028eddf56
            col_center, row_center, fname = photdata[0][ii], photdata[1][ii], photdata[2][ii]
            if col_center < 54 or col_center > 2089 or row_center < 10 or row_center > 2038 :
                continue
            with open(fname,'a') as fout_phot:
<<<<<<< HEAD
                trunc_col_center = np.around(col_center)
                trunc_row_center = np.around(row_center)
=======
                trunc_col_center = sp.around(col_center)
                trunc_row_center = sp.around(row_center)
>>>>>>> 7a22a11ef1034de2480b1598802c4de028eddf56
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
                f1,bkg1,f2,bkg2,f3,bkg3 = p.small_circle_phot(col_center - cmin, row_center-rmin)
                fout_phot.write('{:15.2f} {:10.2f} {:15.2f} {:10.2f} {:15.2f} {:10.2f}\n'.format(f1,bkg1,f2,bkg2,f3,bkg3) )


def main():
    
    args = get_inputs(sys.argv[1:])
    photdata = get_photdata(args.photfile)

    for fname in photdata[2]:
        with open(fname,'w') as fout_phot:
            fout_phot.write('#{:>47s}{:>48s}{:>48s}{:>48s}{:>26s}{:>27s}{:>27s}\n'.format('ap1','ap2','ap3','ap4','ap5','ap6','ap7'))
            for ii in range(2):
                if ii == 0:
                    fout_phot.write('#{:>14s} {:>10s} {:>10s} {:>10s}'.format('flux','bkg','col','row'))
                else:
                    fout_phot.write('{:>15s} {:>10s} {:>10s} {:>10s}'.format('flux','bkg','col','row'))
            fout_phot.write('{:>15s} {:>10s} {:>15s} {:>10s} {:>15s} {:>10s}'.format('flux','bkg','flux','bkg','flux','bkg'))
            fout_phot.write('\n')

    for infile in args.infiles:
        do_phot(infile, photdata)
    
if __name__ == '__main__':
    main()
