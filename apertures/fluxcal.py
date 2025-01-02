#!/usr/bin/env python
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import numpy as np
from astropy.io import fits
import argparse
import os
import sys
sys.path.insert(0, os.environ.get('PIPELINE_DIR') )

import matplotlib.pyplot as plt


from apertures.pixelstamp import PixelStamp


def get_inputs(args):
    parser = argparse.ArgumentParser(
        description="program to try a couple box apertures and calculate centroids")
    parser.add_argument('--photfile', help='Input file of sources and coords, matches phot.data for ISIS')
    parser.add_argument('--infiles', nargs="*", help="list of input files for photometr, append to lc file in this order")
    parser.add_argument('--plot',action='store_true',
                        help='If set, display plots of total scene.')
    parser.add_argument('-d','--diagnostics',action='store_true',
                        help='If set, display diagnostic plots for each iteration of PSF fit.')
        #could add aperture options, etc.
        

    return parser.parse_args()

def get_photdata(photfile):
    with open(photfile,'r') as fin:
        cols,rows, names = [],[],[]
        for line in fin.readlines():
            col,row,_,_,name,_ = line.split()
            s = name.split('/')
            #names.append(  os.path.join(s[0], 'ap_'+s[1])  )
            names.append(s[1])
            cols.append(float(col))
            rows.append(float(row))

    return [np.array(cols),
            np.array(rows),
            names]

def make_regions():
    bkg_aperture = np.zeros((15,15),dtype=bool)
    bkg_aperture[0:5,:] = 1
    bkg_aperture[:,0:5] = 1
    bkg_aperture[11:,:] = 1
    bkg_aperture[:,11:] = 1

    return bkg_aperture


def do_fluxcal(im, photdata, plot=False,diagnostics = False):
    fmt = '{:15.2f} {:10.2f} {:10.4f} {:10.4f}'

        
    bkg_aperture = make_regions()

    with open('ref_gaussian_psf_flux.txt','w') as outfile:
        for ii in range(np.shape(photdata)[1]):            
            col_center, row_center, fname = photdata[0][ii], \
                                                photdata[1][ii], photdata[2][ii]
            print(fname,col_center,row_center)

            
            #if col_center < 61 or col_center > 2082 or row_center < 17 or row_center > 2031 :
            #    continue


            trunc_col_center = int(col_center)
            trunc_row_center = int(row_center)
            cmin = int(trunc_col_center - 7)
            cmax = int(trunc_col_center + 7)
            rmin = int(trunc_row_center - 7)
            rmax = int(trunc_row_center + 7)

            if cmin < 0:
                cmin = 0
            if rmin < 0:
                rmin = 0
            if cmax > 2136:
                cmax = 2136
            if rmax > 2047:
                rmax = 2047

            

            p = PixelStamp(im[rmin:rmax + 1,
                              cmin:cmax + 1])
            
            _a, _b, bkg = p.estimate_bkg(p.image[bkg_aperture])
            cts  = p.fit_scene(col_center - trunc_col_center + (cmax - cmin)//2,
                               row_center - trunc_row_center + (rmax - rmin)//2,
                               bkg, 
                               plot=plot,
                               diagnostic_plots = diagnostics)

            outfile.write('{:15s} {:15.2f}\n'.format(photdata[2][ii] , cts) )
                


def main():
    
    args = get_inputs(sys.argv[1:])
    photdata = get_photdata(args.photfile)

    for infile in args.infiles:
        fhandle = fits.open(infile)
        im = fhandle[0].data
        do_fluxcal(im, photdata, 
                   plot=args.plot,diagnostics = args.diagnostics)


if __name__ == '__main__':
    main()
