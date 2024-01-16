import numpy as np
from astropy.io import fits

imlist = np.genfromtxt('dates',usecols=(0),dtype=str)

for im in imlist:
    fin = fits.open(im)
    fin2 = fits.open('interp_'+im)

    hdu0 = fits.PrimaryHDU(data=fin2[0].data, header=fin[0].header)
    hdu1 = fin[1]

    hdu_list = fits.HDUList([hdu0,hdu1])
    hdu_list.writeto('interp_'+im,checksum=True,overwrite=True)

