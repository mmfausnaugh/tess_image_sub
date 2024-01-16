import scipy as sp
import matplotlib.pyplot as plt
from astropy.io import fits

from apertures.pixelstamp import PixelStamp

import sys
import os
import argparse


#inspect diagnostics related to the background.  input a phot.data
#file---follows algorithm in lc_ap_phot.py to locate the image and
#select background pixels.  Uses the ISIS style of indexing to grab
#background pixels and (a) look at image, look at bkg pixel
#distribution, and make some guesses about how to clip

#note that lc_ap_phot put 0,0 as the lower left of the lower left
#pixel.  But I think ISIS might be center of lower left pixel?

def get_inputs(args):
    parser = argparse.ArgumentParser(
        description="program to try a couple box apertures and calculate centroids")
    parser.add_argument('--photfile', help='Input file of sources and coords, matches phot.data for ISIS')
    parser.add_argument('--infiles', nargs="*", help="list of input files for photometr, append to lc file in this order")
        #could add aperture options, etc.


    return parser.parse_args()


rad_1 = 4.0
rad_2 = 8.0



args = get_inputs(sys.argv[1:])


col,row = sp.genfromtxt(args.photfile,unpack=1,usecols=(0,1) )
names    = sp.genfromtxt(args.photfile,unpack=1,usecols=(4),dtype=str )



for infile in args.infiles:
    f = fits.open(infile)
    fin = infile.split('-')[1]

    for ii in range(len(names)):
        #F,(ax1,ax2,ax3) = plt.subplots(1,3)
        F,(ax1,ax2) = plt.subplots(1,2)

        #get the stamp, make the pixel object
        #hardcoded to 15x15
        trunc_col_center = sp.around(col[ii])
        trunc_row_center = sp.around(row[ii])
        cmin = int(trunc_col_center - 7)
        cmax = int(trunc_col_center + 7)
        rmin = int(trunc_row_center - 7)
        rmax = int(trunc_row_center + 7)

        p = PixelStamp(f[0].data[rmin:rmax + 1,
                                 cmin:cmax + 1])

        annulus_mask = p.select_annulus_pixels(rad_1, rad_2)
        ax1.imshow(p.image,origin = 'lower')
        x = sp.ravel(p.C[annulus_mask])
        y = sp.ravel(p.R[annulus_mask])

        bkg_flux = sp.ravel(p.image[annulus_mask])
        isis_bkg = sp.median(bkg_flux)
        sextractor_bkg = 2.5*sp.median( bkg_flux ) - 1.5*sp.mean(bkg_flux)
        diff = isis_bkg - sextractor_bkg

        ax1.plot(x,y,'ko',mfc='2',ms=4)
        ax1.set_title('{} {}'.format(names[ii],fin))

        ax2.hist(bkg_flux)
        yl,yh = ax2.get_ylim()
        ax2.plot([isis_bkg,isis_bkg],[yl,yh],'r--',label='ISIS')
        ax2.plot([sextractor_bkg,sextractor_bkg],[yl,yh],'--',
                 color='orange',label='sextractor')
        xl,xh = ax2.get_xlim()
        #ax2.text(0.2*xh,0.8*yh,'diff = {:.0f}'.format(diff),fontsize=18)
        ax2.set_title('ISIS $-$ sextractor = {:.0f}'.format(diff),fontsize=18)
        ax2.legend()

        F.set_size_inches(12,6)

        plt.savefig('{}_{}_bkg_inspect.png'.format(names[ii],fin))
    f.close()
