#!/usr/bin/env python
import scipy as sp
from astropy.io import fits
import argparse
import sys
import os
from scipy.stats import sigmaclip, mode

import matplotlib.pyplot as plt
    

def get_inputs(args):
    parser = argparse.ArgumentParser( description="Uses COA results to sum counts in optimal aperture and subtract the background")
    parser.add_argument("--infile", help="COA results file")
    parser.add_argument("--outdir", default='./', help="location for output file")
    return parser.parse_args()


def main():

    args = get_inputs(sys.argv[1:])


    catID, target, ra, dec, mag, flux_frac, crowding, oa_rows, oa_cols, ref_row, ref_col = sp.genfromtxt(args.infile,unpack=1,dtype=str)

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

    #this file can be at the sector level, since it is filtered on name
    fout = open('coa_phot.reg','w')

    fmt='{:15d} {:>10s} {:15.6f} {:15.6f} {:15.4f} {:15.2f} {:15.2f} {:15.2f} {:15.2f} {:15d} {:15.6f} {:15.6f}\n'


    for ii in range(len(target)):
        oa_rows_use = sp.array([  int(s) for s in oa_rows[ii].split(',')[0:-1] ])
        oa_cols_use = sp.array([  int(s) for s in oa_cols[ii].split(',')[0:-1] ])


        for z in zip(oa_cols_use,oa_rows_use):
            fout.write('point {} {} \n'.format(z[0],z[1]))
    
    fout.close()


if __name__ == '__main__':
    main()
