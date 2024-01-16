import numpy as np
from astropy.io import fits
import sys

fin = fits.open(sys.argv[1])
fin2 = fits.open('ref.fits')

hdu0 = fits.PrimaryHDU(data=fin2[0].data, header=fin[0].header)
#hdu1 = fin[1]

hdu_list = fits.HDUList([hdu0])
hdu_list.writeto('ref.fits', checksum=True, overwrite=True)

