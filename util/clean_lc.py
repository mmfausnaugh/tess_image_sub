#!/usr/bin/env python
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import numpy as np
import scipy as sp
from scipy.ndimage import median_filter
import matplotlib.pyplot as plt
import sys
import re
import glob

sys.path.insert(0,'/pdo/users/faus')

from catalog2tess_px.catalogs.TNS import TNS
from catalog2tess_px.catalogs.HyperLedaCsv import HyperLedaCsv
from catalog2tess_px.catalogs.GaiaCsv import GaiaCsv
from catalog2tess_px.catalogs.MilliquasCsv import MilliquasCsv

import argparse

from tess_time.cut_ffi.cut_data import cut_data, cut_multisector_data, bad_calibration2TJD
from tess_time.btjd.btjd_correction import btjd_correction

catalog_lookup = {
        'discovery':TNS,
        'prediscovery':TNS,
        'postdiscovery':TNS,
        'gaia_vars':GaiaCsv,
        'hyperleda':HyperLedaCsv,
        'milliquas':MilliquasCsv,
}

#first element is the directory in catalog2tess_px to look up, second
#element is the formula for the individual file names
catalog_directory_lookup = {
    'discovery':    ['TNS','s{:02d}/sector{}_cam{}_transients.txt'],
    'prediscovery': ['TNS','s{:02d}/sector{}_cam{}_transients.txt'],
    'postdiscovery':['TNS','s{:02d}/sector{}_cam{}_transients.txt'],
    'gaia_vars':    ['Gaia','s{:02d}/gaia_dr2_s{:02d}_cam{}.txt'],
    'hyperleda':    ['HyperLEDA','s{:02d}/hyperleda_s{:02d}_cam{}.txt'],
    'milliquas':    ['Milliquas','s{:02d}/milliquas_s{:02d}_cam{}.txt'],
}

def parse_sector_cam_ccd_cat(ifile):
        wdir = os.path.abspath(os.path.dirname(ifile))
        sector_search = re.search('sector(\d\d)',wdir)
        sector = sector_search.group(1)

        #cam, ccd number
        cam_search = re.search('cam(\d)',wdir)
        cam = cam_search.group(1)
        ccd_search = re.search('ccd(\d)',wdir)
        ccd = ccd_search.group(1)

        cat_search = re.search('lc_(\w*)', wdir)
        cat_identity = cat_search.group(1)
        catuse = catalog_lookup[cat_identity]
        return sector, cam, ccd, catuse, cat_identity

def make_catalog_object(catuse, cat_identity, sector, cam):
        catfile = find_catalog_file(cat_identity,sector,cam)
        cat = catuse(catfile,ignore_image_buffer=True)
        return cat



def find_catalog_file(cat_identity,sector,cam):
    dstem = catalog_directory_lookup[cat_identity]
    return os.path.join('/pdo/users/faus/python/catalog2tess_px/',
                        dstem[0],
                        dstem[1].format(int(sector),int(sector), cam)
    )

def get_meta_data(ifile, cat):
    wdir  =  os.path.abspath( os.path.dirname(ifile))

    print(ifile)
    obj_search = re.search('lc_(.*)', os.path.basename(ifile) )
    obj = obj_search.group(1)

    if 'detrended' in obj:
        obj = obj.split('_')[-2]
    
    #    m = np.in1d(cat.obj_name, np.uint64(obj) )'    
    print('looking for obj:',obj)
    if isinstance(cat.obj_name[0], np.uint64):
        m = np.in1d(cat.obj_name, np.uint64(obj) )
    else:
        m = np.in1d(cat.obj_name, obj )
    return {'name':cat.obj_name[m][0], 
            'RA':cat.ra[m][0],
            'DEC':cat.dec[m][0]
    }

def get_fluxcal(fluxcal_file, light_curve_name):
    lc_names = np.genfromtxt(fluxcal_file,usecols=(0),dtype=str)
    fluxes   = np.genfromtxt(fluxcal_file,usecols=(1) )
    if fluxes.size == 1:
        fluxes = np.array([fluxes])

    if 'detrended' in light_curve_name:
        light_curve_name = 'lc_' + light_curve_name.split('_')[-2]
    #obj_list = []
    #for lc_name in lc_names:
    #    obj_search =re.search('lc_(.*)',os.path.basename(ifile))
    #    obj = obj_search.group(1)
    #    #print('lookup obj',obj)
    #    if obj == 'detrended':
    #        obj = ifile.split('_')[-2]
    #    #print(obj)
    #    obj_list.append(obj)
    #
    #m= np.in1d(obj_list, object_use)

    m = np.in1d(lc_names, light_curve_name.split('/',1) )
    #print(lc_names)
    #print(fluxes)
    #print(m)

    assert len(fluxes[m]) == 1

    return fluxes[m]


def match_times(x1,x2):
        m1 = np.in1d(x1,x2)
        m2 = np.in1d(x2,x1[m1])
        return m1,m2
    
def clean_lc(ifile, metadata, 
             multisector=False,
             reference_flux = None):

    x,y,z,bkg = np.genfromtxt(ifile,unpack=1,usecols=(0,1,2,6))

    #remove gaps
    wdir = os.path.abspath(os.path.dirname(ifile))

    if not multisector:
        sector_idx = wdir.find('sector')
        sector     = wdir[sector_idx : sector_idx+8]
        cam_idx = wdir.find('cam')
        cam = wdir[cam_idx : cam_idx+4]
        ccd_idx = wdir.find('ccd')
        ccd = wdir[ccd_idx : ccd_idx+4]

        bad_cal_times = bad_calibration2TJD(ifile)
        x2,y2,z2, = cut_data(x,y,z, sector, cam, ccd, 
                             bad_cal_times = bad_cal_times)

        x2,bkg2,z2, = cut_data(x,bkg,z, sector, cam, ccd,
                               bad_cal_times = bad_cal_times)
        if int(sector[-2:]) < 56:
                if int(sector[-2:]) < 27:
                        exptime = 30.0/60./24.0
                        median_filter_size=48

                else:
                        exptime = 10.0/60./24.0
                        median_filter_size=int(48*3/2.) #1/2 day filtering

        else:
                exptime = 200.0/3600./24.0
                median_filter_size=int(48*9/4.) #1/4 day filtering


    else:
            x2,y2,z2,   = cut_multisector_data(x,y,z, )
            x2,bkg2,z2, = cut_multisector_data(x,bkg,z)

            exptime = np.ones(len(x2))
            #roughly the start of s27
            exptime[ x2  < 2036.10 ] = 30.0/60./24.0
            exptime[ (x2 >= 2036.10) & (x2 <=2825.4) ] = 10.0/60./24.0
            exptime[ x2 > 2825.4 ] = 200.0/3600./24.

            

    #load up the filtered background estimate, if it exists
    dstem,dtarget = os.path.split(wdir)
    ifile2 = os.path.join(dstem,'bkg_phot',dtarget,os.path.basename(ifile))
    if 'detrended' in ifile2:
        ifile2 = ifile2[0:-10]
    if os.path.isfile(ifile2):
        x_bkg,y_bkg,z_bkg,bkg_bkg = np.genfromtxt(ifile2, unpack=1,usecols=(0,1,2,6))

        #remove gaps
        x_bkg2,y_bkg2,z_bkg2   = cut_data(x_bkg, y_bkg,z_bkg, sector, cam, ccd,
                                          bad_cal_times = bad_cal_times)
        x_bkg2,bkg_bkg2,z_bkg2 = cut_data(x_bkg, bkg_bkg,z_bkg, sector, cam, ccd,
                                          bad_cal_times = bad_cal_times)
        bkg_model = median_filter(y_bkg2, size=median_filter_size, mode='reflect')
    else:
        x_bkg2 = x2
        y_bkg2 =    np.array([np.nan]*len(x2))
        z_bkg2 =    np.array([np.nan]*len(x2))
        bkg_bkg2  = np.array([np.nan]*len(x2))
        bkg_model = np.array([np.nan]*len(x2))



    #some times, a little bit of data is missing in one or the other
    #file.  this forces everythin to match
    m1,m2 = match_times(x2,x_bkg2)
    x2,y2,z2,bkg2 = x2[m1],y2[m1],z2[m1],bkg2[m1]
    x_bkg2,y_bkg2, bkg_bkg2,z_bkg2,bkg_model = x_bkg2[m2],y_bkg2[m2], bkg_bkg2[m2],z_bkg2[m2],bkg_model[m2]

    
    #correct to mid exposure
    #convert to BTJD
    #would like to save x2, for look up later


    print(exptime)
    x_correct = btjd_correction(x2 + exptime/2.0, metadata['RA'], metadata['DEC'] )

#    print('saving {}'.format(os.path.splitext(ifile)[0]+'_cleaned'))
    #adding this Nov 22, 2022. If fluxcal is set, we want magnitudes
    #and counts per second in the light curves
    if reference_flux is not None:
        print('saving {}'.format(ifile+'_cleaned'))

        if reference_flux > 0:
            y2 = reference_flux - y2
        else:
            #this means reference flux is zero or negative
            #essentially, quite small
            y2 = -y2


        inttime = exptime*0.8*0.99*86400
        y2 = y2/inttime
        z2 = z2/inttime
        bkg2 = -bkg2/inttime
        bkg_model = -bkg_model/inttime
        y_bkg2 = -y_bkg2/inttime
        z_bkg2 = z_bkg2/inttime

        mag = np.zeros(len(y2))
        emag = np.zeros(len(y2))

        #set mag limits based on 3sigma relative to uncertainties
        #negative flux will be treated as an upper limit (3sigma)
        mask = y2 < z2*3
        mag[mask]  = -2.5*np.log10(z2[mask]*3) + 20.44
        emag[mask] = 99.9

        mag[~mask]  = -2.5*np.log10(y2[~mask]) + 20.44
        emag[~mask] = z2[~mask]/y2[~mask]*2.5/np.log(10)


        print(reference_flux/inttime)
        np.savetxt(ifile+'_cleaned',np.c_[x_correct, x2, y2, z2, mag, emag, bkg2,  bkg_model, y_bkg2, z_bkg2],
                   fmt='%15.5f %15.5f %15.4f %15.4f %15.4f %15.4f %15.4f %15.4f %15.6f %15.6f',
                   header='reference_flux: {:15.4f}\n{:>13s} {:>15s} {:>15s} {:>15s} {:>15s} {:>15s} {:>15s} {:>15s} {:>15s} {:>15s}'.format(reference_flux[0]/inttime, 'BTJD','TJD','cts_per_s','e_cts_per_s','mag','e_mag','bkg','bkg_model', 'bkg2','e_bkg2'))

    else:
            print('saving {}'.format(ifile + '_cleaned'))

            np.savetxt(ifile+'_cleaned',np.c_[x_correct, x2, -y2, z2,-bkg2, -bkg_model, -y_bkg2, z_bkg2],
                       fmt='%15.5f %15.5f %15.4f %15.4f %15.4f %15.4f %15.4f %15.4f',
                       header='{:>13s} {:>15s} {:>15s} {:>15s} {:>15s} {:>15s} {:>15s} {:>15s}'.format('BTJD','TJD',
                                                                                                       'cts','e_cts',
                                                                                                       'bkg','bkg_model',
                                                                                                       'bkg2','e_bkg2'),
                       comments='')


def get_inputs(args):
    parser = argparse.ArgumentParser( description="Specify TNS, hyperleda, milliquas, or gaia light curves to plot---will look up the source in the catalogs and display metadata.")
    parser.add_argument('infiles', nargs='+')
    parser.add_argument('--fluxcal', default=None, help='Set to name of file with fluxcalibration.  Expects to find light curve names identical to what is in phot.data')
    return parser.parse_args()
    
def main():
    args = get_inputs(sys.argv[1:])
#    if len(args.infiles) == 1:            
#        if 'lc_*' in args.infiles[0]:
#            print('no input files, exiting')
#            sys.exit()

    #don't get rid of any loaded catalogs, or else code is slow
    loaded_cats = {}

    for ifile in args.infiles:
        print(ifile)
        if '.png' in ifile:
            continue
        if '_cleaned' in ifile:
            continue
        if os.path.isdir(ifile):
            continue
        #handles case where you run on lc_{,pre,post}discovery/lc_* all at once, but
        #one of those directories is empty
        if 'lc_*' in ifile:
            continue
        #lc type, for catalog  look up
        sector, cam, ccd, cat_use, cat_identity = parse_sector_cam_ccd_cat(ifile)

        if cat_identity in loaded_cats.keys():
            if sector in loaded_cats[cat_identity].keys():
                if cam in loaded_cats[cat_identity][sector].keys():
                    #catalog is already loaded
                    cat = loaded_cats[cat_identity][sector][cam]
                else:
                    #dictionary has cat_identity and sector but no catalog for the specified camera
                    loaded_cats[cat_identity][sector][cam] = make_catalog_object(cat_use, cat_identity, sector,cam)
                    cat = loaded_cats[cat_identity][sector][cam]
            else:
                #dictionary has cat_identity but no catalogs for the specified sector
                loaded_cats[cat_identity][sector] = {}
                loaded_cats[cat_identity][sector][cam] = make_catalog_object(cat_use, cat_identity, sector,cam)
                cat = loaded_cats[cat_identity][sector][cam]
        else:
            #dictionary does not have any catalogs for cat_identity
            loaded_cats[cat_identity] = {}
            loaded_cats[cat_identity][sector] = {}
            loaded_cats[cat_identity][sector][cam] = make_catalog_object(cat_use, cat_identity, sector,cam)
            cat = loaded_cats[cat_identity][sector][cam]            



        metadata = get_meta_data(ifile, cat)
        if args.fluxcal is not None:
            reference_flux = get_fluxcal(args.fluxcal, ifile )
        else:
            reference_flux = None
        clean_lc(ifile,metadata, reference_flux = reference_flux)


if __name__== '__main__':
    main()

#for i in 1 3; do for  j in 1 2 3 4; do cd cam${i}_ccd${j}; pwd; for d in discovery postdiscovery prediscovery; do cp lc_${d}/phot.data . ; mkdir lc; python ~/image_sub/ap_phot.py; mv lc/ref.phot lc_${d}/ref.phot; done ; cd ..; done; done
