#!/usr/bin/env python
import numpy as np
from astropy.io import fits
import argparse
import sys
import os

import matplotlib.pyplot as plt


from apertures.pixelstamp import PixelStamp


def get_inputs(args):
    parser = argparse.ArgumentParser(
        description="program to try a couple box apertures and calculate centroids")
    parser.add_argument('--photfile', help='Input file of sources and coords, matches phot.data for ISIS')
    parser.add_argument('--infiles', nargs="*", help="list of input files for photometr, append to lc file in this order")
    parser.add_argument('--plot',action='store_true',
                        help='If set, display a plot with '
                        'background subtracted image array'
                        'and pixel value distributions')
    parser.add_argument('--diff',action='store_true',
                        help='If set, assumes difference images and'
                        ' will not trim the background pixel distribution'
                        ' to avoid crowding and blending biases')
        #could add aperture options, etc.
        

    return parser.parse_args()

def get_photdata(photfile):
    with open(photfile,'r') as fin:
        cols,rows, names = [],[],[]
        for line in fin.readlines():
            col,row,_,_,name,_ = line.split()
            s = name.split('/')
            names.append(  os.path.join(s[0], 'ap_'+s[1])  )
            cols.append(float(col))
            rows.append(float(row))

    return [np.array(cols),
            np.array(rows),
            names]

def make_regions():
    bkgs = np.zeros((6,15,15),dtype=bool)
    bkgs[:,0:2,:] = 1
    bkgs[:,:,0:2] = 1
    bkgs[:,13:,:] = 1
    bkgs[:,:,13:] = 1

    aps = np.zeros((6,15,15),dtype=bool)
    #defaults to 1x1, 3x3
    #5x5, 7x7,  9x9,
    #and 11x11
    aps[0,7,7] = 1
    aps[1,6:9,6:9] = 1
    aps[2,5:10,5:10] = 1
    aps[3,4:11,4:11] = 1
    aps[4,3:12,3:12] = 1
    aps[5,2:13,2:13] = 1
    return aps,bkgs


def do_phot(infile, photdata, plot=False,diff=False):
    fmt = '{:15.2f} {:10.2f} {:10.4f} {:10.4f}'
    with fits.open(infile) as fhandle:
        im = fhandle[0].data
        print(infile)
        #make a bunch of apertures and background regions
        aps,bkgs = make_regions()


        for ii in range(np.shape(photdata)[1]):            
            col_center, row_center, fname = photdata[0][ii], photdata[1][ii], photdata[2][ii]
            if col_center < 54 or col_center > 2089 or row_center < 10 or row_center > 2038 :
                continue
            with open(fname,'a') as fout_phot:
                fout_phot.write(infile+ '  ')
                trunc_col_center = np.around(col_center)
                trunc_row_center = np.around(row_center)
                cmin = int(trunc_col_center - 7)
                cmax = int(trunc_col_center + 7)
                rmin = int(trunc_row_center - 7)
                rmax = int(trunc_row_center + 7)

                p = PixelStamp(im[rmin:rmax + 1,
                                  cmin:cmax + 1])
                for ii,(ap_use,bkg_use) in enumerate(zip(aps,bkgs)):
                    if ii == 5 and plot==True:
                        fout,bkg,col,row = p.compute_phot(ap_use, bkg_use, 
                                                          plot=True,
                                                          diff=diff)
                    else:
                        fout,bkg,col,row = p.compute_phot(ap_use, bkg_use,
                                                          diff=diff)
                    col += col_center
                    row += row_center
                    fout_phot.write( fmt.format(fout,bkg,col,row) )
                    #see https://photutils.readthedocs.io/en/stable/pixel_conventions.html
                    #for coordinate convention
                    #it is 0,0 = center of lower left pixel
                    #so, that matches ISIS and the phot.data 
                    #file
                f1,bkg1,f2,bkg2,f3,bkg3 = p.small_circle_phot(col_center - cmin, row_center-rmin)
                fout_phot.write('{:15.2f} {:10.2f} {:15.2f} {:10.2f}'.format(
                    f1,bkg1,f2,bkg2) )
                f1,bkg1,f2,bkg2,f3,bkg3 = p.circle_phot(col_center - cmin, row_center-rmin)
                fout_phot.write('{:15.2f} {:10.2f} {:15.2f} {:10.2f} '\
                                '{:15.2f} {:10.2f}\n'.format(f1,bkg1,f2,bkg2,f3,bkg3) )


def main():
    
    args = get_inputs(sys.argv[1:])
    photdata = get_photdata(args.photfile)

    for fname in photdata[2]:
        print(fname)
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
        do_phot(infile, photdata, plot=args.plot, diff=args.diff)
    
if __name__ == '__main__':
    main()
