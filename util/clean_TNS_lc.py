#!/usr/bin/env python
import scipy as sp
from scipy.ndimage import median_filter
import matplotlib.pyplot as plt
import os
import sys
import re
import glob
sys.path.insert(0,'/pdo/users/faus')
from catalog2tess_px.catalogs.TNS import TNS
import argparse
from tess_time.cut_ffi.cut_data import cut_data
from tess_time.btjd.btjd_correction import btjd_correction



def get_meta_data(ifile):
    wdir  =  os.path.abspath( os.path.dirname(ifile))

    #sector number
    sector_search = re.search('sector(\d\d)',wdir)
    sector = sector_search.group(1)

    #cam, ccd number
    cam_search = re.search('cam(\d)',wdir)
    cam = cam_search.group(1)
    ccd_search = re.search('ccd(\d)',wdir)
    ccd = ccd_search.group(1)

    
    cat = TNS('/pdo/users/faus/python/catalog2tess_px/TNS/s{:02d}/sector{}_cam{}_transients.txt'.format(int(sector), int(sector), cam))

    obj = ifile.split('_')[-1]
    if obj == 'detrended':
        obj = ifile.split('_')[-2]        
    m = sp.in1d(cat.obj_name, obj)
    print(obj)
    print(any(m))
    return {'prefix':cat.prefix[m][0], 
            'name':cat.obj_name[m][0], 
            'group':cat.group[m][0], 
            'tjd':cat.tjd[m][0],
            'mag':cat.mag[m][0], 
            'fband':cat.fband[m][0], 
            'z':cat.z[m][0],
            'internal_name':cat.internal_name[m][0],
            'obj_type':cat.obj_type[m][0],
            'sector':sector,
            'cam':cam,
            'ccd':ccd,
            'RA':cat.ra[m][0],
            'DEC':cat.dec[m][0]
            }



def clean_lc(ifile, metadata):
    x,y,z,bkg = sp.genfromtxt(ifile,unpack=1,usecols=(0,1,2,6))

    wdir = os.path.abspath(os.path.dirname(ifile))
    sector_idx = wdir.find('sector')
    sector     = wdir[sector_idx : sector_idx+8]
    cam_idx = wdir.find('cam')
    cam = wdir[cam_idx : cam_idx+4]
    ccd_idx = wdir.find('ccd')
    ccd = wdir[ccd_idx : ccd_idx+4]

    #remove gaps
    x2,y2,z2, = cut_data(x,y,z, sector,cam,ccd)
    x2,bkg2,z2, = cut_data(x,bkg,z, sector, cam, ccd)

    #load up the filtered background estimate, if it exists
    dstem,dtarget = os.path.split(wdir)
    ifile2 = os.path.join(dstem,'bkg_phot',dtarget,os.path.basename(ifile))
    if 'detrended' in ifile2:
        ifile2 = ifile2[0:-10]
    print(ifile2)
    if os.path.isfile(ifile2):
        x_bkg,y_bkg,z_bkg,bkg_bkg = sp.genfromtxt(ifile2, unpack=1,usecols=(0,1,2,6))

        #remove gaps
        x_bkg2,y_bkg2,z_bkg2   = cut_data(x_bkg, y_bkg,z_bkg, sector, cam, ccd)
        x_bkg2,bkg_bkg2,z_bkg2 = cut_data(x_bkg, bkg_bkg,z_bkg, sector, cam, ccd)
        bkg_model = median_filter(y_bkg2, size=48, mode='reflect')
    else:
        y_bkg2 =   sp.array([sp.nan]*len(x2))
        z_bkg2 =   sp.array([sp.nan]*len(x2))
        bkg_bkg2 = sp.array([sp.nan]*len(x2))
        bkg_model = sp.array([sp.nan]*len(x2))


    #correct by 15 minutes to mid exposure
    #convert to BTJD
    #would like to save x2, for look up later
    x_correct = btjd_correction(x2 + 0.25/24.0, metadata['RA'], metadata['DEC'] )

    print('saving {}'.format(os.path.splitext(ifile)[0]+'_cleaned'))

#    sp.savetxt(os.path.splitext(ifile)[0]+'_cleaned',sp.c_[x_correct, x2, -y2, z2,-bkg2, -y_bkg2, z_bkg2, -bkg_bkg2],
#               fmt='%15.5f %15.5f %15.4f %15.4f %15.4f %15.4f %15.4f %15.4f',
#               header='{:>13s} {:>15s} {:>15s} {:>15s} {:>15s} {:>15s} {:>15s} {:>15s}'.format('BTJD','TJD',
#                                                                                               'cts','e_cts','bkg',
#                                                                                               'bkg2','e_bkg2','bkg_bkg'))
#it seems as though the bkg_bkg is very similar to bkg (as it should be!).  so we won't bother saving it
#do I median smooth y_bkg2 here?
    sp.savetxt(os.path.splitext(ifile)[0]+'_cleaned',sp.c_[x_correct, x2, -y2, z2,-bkg2, -bkg_model, -y_bkg2, z_bkg2],
               fmt='%15.5f %15.5f %15.4f %15.4f %15.4f %15.4f %15.4f %15.4f',
               header='{:>13s} {:>15s} {:>15s} {:>15s} {:>15s} {:>15s} {:>15s} {:>15s}'.format('BTJD','TJD',
                                                                                               'cts','e_cts','bkg','bkg_model',
                                                                                               'bkg2','e_bkg2'))


def get_inputs(args):
    parser = argparse.ArgumentParser( description="Specify TNS light curves to plot---will look up the source in the catalogs and display metadata.")
    parser.add_argument('--SN',action='store_true',help='If set, only plot confirmed SNe in TNS')
    parser.add_argument('infiles', nargs='+')
    return parser.parse_args()
    
def main():
    args = get_inputs(sys.argv[1:])

    for ifile in args.infiles:

        if '.png' in ifile:
            continue
        if '_cleaned' in ifile:
            continue

        metadata = get_meta_data(ifile)
        if args.SN:
            #check if the prefix is a SN.  If not, move to next in the
            #loop
            if metadata['prefix'] != 'SN':
                continue

        clean_lc(ifile,metadata)


if __name__== '__main__':
    main()

#for i in 1 3; do for  j in 1 2 3 4; do cd cam${i}_ccd${j}; pwd; for d in discovery postdiscovery prediscovery; do cp lc_${d}/phot.data . ; mkdir lc; python ~/image_sub/ap_phot.py; mv lc/ref.phot lc_${d}/ref.phot; done ; cd ..; done; done
