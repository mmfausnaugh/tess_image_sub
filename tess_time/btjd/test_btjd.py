import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
import os
import glob

from btjd_correction import *

dstem = '/pdo/spoc-data/sector-032/ffis'
#ffis = glob.glob(dstem + '/*-1-1-*ffic.fits.gz')
ffis = ['tess2020325180911-s0032-4-1-0200-s_ffic.fits.gz',
        'tess2020325184911-s0032-4-1-0200-s_ffic.fits.gz',
        'tess2020325180911-s0032-4-1-0200-s_ffic.fits.gz',
        'tess2020326180911-s0032-4-1-0200-s_ffic.fits.gz',
        'tess2020327180911-s0032-4-1-0200-s_ffic.fits.gz',
        'tess2020328180911-s0032-4-1-0200-s_ffic.fits.gz',
        'tess2020329180911-s0032-4-1-0200-s_ffic.fits.gz',
        'tess2020351161910-s0032-4-1-0200-s_ffic.fits.gz',
        'tess2020351170910-s0032-4-1-0200-s_ffic.fits.gz']

print('{:>15s} {:>15s} {:>15s} {:>15s} {:>15s}'.format('btjd','spoc_btjd',
                                                      'spoc_barycor',
                                                      'me_cor','input'))
#for ffi in ffis[::100]:
for ffi in ffis:
#    print(ffi)

    f = fits.open(dstem + '/' + ffi)
    spoc_cor = f[1].header['BARYCORR']
    spoc_midbtjd = np.mean([f[1].header['TSTART'] , f[1].header['TSTOP']])
    spoc_midtjd = spoc_midbtjd - spoc_cor
    w = WCS(f[1].header)
    ra,dec = w.all_pix2world([1068.],[1024],1)
    ra = ra[0]
    dec = dec[0]
#print(ra_dec)
#ra = ra_dec.data.lon.deg[0]
#dec = ra_dec.data.lat.deg[0]
#print(ra,dec)
    
#    print(spoc_midtjd)
    new_time = btjd_correction(spoc_midtjd,
                               ra,
                               dec)

    #    print(new_time,spoc_midbtjd,spoc_cor,new_time -spoc_midbtjd,spoc_midtjd)
    print('{:15.6f} {:15.6f} {:15.6f} {:15.6f} {:15.6f}'.format(new_time, spoc_midbtjd, 
                                                                86400*spoc_cor, 
                                                                86400*(new_time - spoc_midtjd), 
                                                                spoc_midtjd))
