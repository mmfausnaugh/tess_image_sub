import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
import matplotlib.pyplot as plt
import sys
import re

image = sys.argv[1]
datafile  = sys.argv[2]
#f = fits.open(image)
f = fits.getheader(image,1)
col,row = np.genfromtxt(datafile,unpack=1,usecols=(1,2))
#wcs = WCS(f[1].header)
wcs = WCS(f)
ra,dec = wcs.all_pix2world(col,row,1.0)
np.savetxt('xy2sky_{}.txt'.format(datafile), np.c_[col,row,ra,dec])
