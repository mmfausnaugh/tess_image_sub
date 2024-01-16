import numpy as np
from astropy.io import fits
import glob

imlist = glob.glob("*fits")

for im in imlist:
    print(im)
    f = fits.open(im)

    header_check = fits.open('../' + im.replace('interp_',''))
    data_check   = fits.open('../' + im)

    for key in header_check[0].header.keys():
        if key == 'CHECKSUM' or key == 'DATASUM':
            continue
        try:
            assert f[0].header[key] == header_check[0].header[key]
        except AssertionError:
            print(key, f[0].header[key],header_check[0].header[key])
            raise

    for key in header_check[1].header.keys():
        if key == 'CHECKSUM':
            continue
        assert f[1].header[key] == header_check[1].header[key]

    assert (f[0].data   == data_check[0].data).all()
    assert (f[1].data   == header_check[1].data).all()
                               
                               
    f.close()
    header_check.close()
    data_check.close()
