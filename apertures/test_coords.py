#!/usr/bin/env python
import numpy as np
from astropy.io import fits
import argparse
import sys
import os

import matplotlib.pyplot as plt


from apertures.pixelstamp import PixelStamp



dummy_image = np.zeros( (15,15) )

p = PixelStamp(dummy_image)

#g1 = np.log10(  p.gaussian(7.5,7.5) )
#g2 = np.log10(  p.gaussian(7.,7.) )
g1 = p.gaussian(7.5,7.5) 
g2 = p.gaussian(7.,7.) 

F,(ax1,ax2) = plt.subplots(1,2)

vl,vh = np.percentile(np.ravel(g1), [5,99.5])
ax1.imshow(g1,vmin = vl, vmax = vh, origin = 'lower')
ax2.imshow(g2,vmin = vl, vmax = vh, origin='lower')

plt.show()
