import scipy as sp
import photutils as phot
from astropy.io import fits

col,row = sp.genfromtxt('phot.data',unpack=1,usecols=(0,1))
lc_name = sp.genfromtxt('phot.data',unpack=1,usecols=(4),dtype=str)

im = fits.getdata('ref.fits')

#python style aperture photometry
ap = phot.CircularAperture( (col,row),r=0.5)
phot_table = phot.aperture_photometry(im,ap,method='exact')

#convert to cts/s and then to mags
cts = sp.array(phot_table['aperture_sum']) - 1.e5*ap.area()
flux = cts/(1800*0.8)
mag = -2.5*sp.log10(flux/15000.0) + 10

#want good control of formating
with open('lc/ref.phot','w') as fout:
    fout.write('{:20s} {:>12s} {:>12s} {:>12s}\n'.format('#LC_name','total_cts','cts/s','mag'))


    try:
        for i in range(len(lc_name)):        
            fout.write('{:20s} {:12.2f} {:12.2f} {:12.6f}\n'.format(lc_name[i], cts[i], flux[i], mag[i]))

    except:
        fout.write('{:20s} {:12.2f} {:12.2f} {:12.6f}\n'.format(lc_name.astype(str), 
                                                                cts[0].astype(float), 
                                                                flux[0].astype(float), 
                                                                mag[0].astype(float)
                                                            ))

