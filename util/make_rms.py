import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import numpy as np
from astropy.io import fits
import os
import re
import sys


def make_rms(inlist ):
    #assumes files in inlist are in current working directory
    avg = 0
    square = 0
    N = 0
    for infile in inlist:
        #dirlook = 'cam{}_ccd{}'.format(cam,ccd)
        #infile_use = glob.glob( dirlook + '/o1a/slice*' + '/conv_tess2023132091625-{:08d}-{}-crm-ffi_ccd{}.cal.fits'.format(int(infile),cam,ccd))[0]
        #print(infile_use)
        #infile_use = glob.glob(dirlook + '/o1a/tess*' + str(infile) + '*')[0]
        #print(dirlook, str(infile), infile_use)

        d = fits.open(infile)[0].data

        avg += d
        square += d**2
        N += 1
    rms = np.sqrt( square/N -  (avg/N)**2   )
    fits.writeto('rms.fits', rms,overwrite=True)

if __name__ == "__main__":
    inlist = np.genfromtxt(sys.argv[1],dtype=str)
    make_rms(inlist)
