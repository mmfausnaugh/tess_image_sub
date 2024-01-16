#!/usr/bin/env python
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
    col,row = sp.genfromtxt(photfile,unpack=1,usecols=(0,1))
    names = sp.genfromtxt(photfile,usecols=(4),dtype=str)
    name_out = []
    for name in names:
        s = name.split('/')
        name_out.append(  os.path.join(s[0], 'ap_'+s[1])  )
    return [col,row,name_out]

def make_regions():
    bkgs = sp.zeros((4,15,15),dtype=bool)
    bkgs[:,0:2,:] = 1
    bkgs[:,:,0:2] = 1
    bkgs[:,13:,:] = 1
    bkgs[:,:,13:] = 1

    aps = sp.zeros((4,15,15),dtype=bool)
    #defaults to 5x5, 7x7, 9x9, and 11x11
    aps[0,5:10,5:10] = 1
    aps[1,4:11,4:11] = 1
    aps[2,3:12,3:12] = 1
    aps[3,2:13,2:13] = 1
    return aps,bkgs


def do_phot(infile, photdata):
    fmt = '{:15.2f} {:10.2f} {:10.4f} {:10.4f}'
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
                f1,bkg1,f2,bkg2,f3,bkg3 = p.circle_phot(col_center - cmin, row_center-rmin)
                fout_phot.write('{:15.2f} {:10.2f} {:15.2f} {:10.2f} {:15.2f} {:10.2f}\n'.format(f1,bkg1,f2,bkg2,f3,bkg3) )


def main():
    
    args = get_inputs(sys.argv[1:])
    photdata = get_photdata(args.photfile)

    for fname in photdata[2]:
        with open(fname,'w') as fout_phot:
            fout_phot.write('#{:>47s}{:>48s}{:>48s}{:>48s}{:>26s}{:>27s}{:>27s}\n'.format('ap1','ap2','ap3','ap4','ap5','ap6','ap7'))
            for ii in range(4):
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
