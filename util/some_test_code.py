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
from catalog2tess_px.catalogs.HyperLedaCsv import HyperLedaCsv
from catalog2tess_px.catalogs.GaiaCsv import GaiaCsv

import argparse

from tess_time.cut_ffi.cut_data import cut_data
from tess_time.btjd.btjd_correction import btjd_correction

catalog_lookup = {
    'discovery':TNS,
    'prediscovery':TNS,
    'postdiscovery':TNS,
    'gaia_vars':GaiaCsv,
    'hyperleda':HyperLedaCsv
}

#first element is the directory in catalog2tess_px to look up, second
#element is the formula for the individual file names
catalog_directory_lookup = {
    'discovery':    ['TNS','s{:02d}/sector{}_cam{}_transients.txt'],
    'prediscovery': ['TNS','s{:02d}/sector{}_cam{}_transients.txt'],
    'postdiscovery':['TNS','s{:02d}/sector{}_cam{}_transients.txt'],
    'gaia_vars':    ['Gaia','s{:02d}/gaia_dr2_s{:02d}_cam{}.txt'],
    'hyperleda':    ['HyperLEDA','s{:02d}/hyperleda_s{:02d}_cam{}.txt']
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
    cat = catuse(catfile)
    return cat



def find_catalog_file(cat_identity,sector,cam):
    dstem = catalog_directory_lookup[cat_identity]
    return os.path.join('/pdo/users/faus/python/catalog2tess_px/',
                        dstem[0],
                        dstem[1].format(int(sector),int(sector), cam)
                    )

def get_meta_data(ifile, cat):
    wdir  =  os.path.abspath( os.path.dirname(ifile))


    obj_search = re.search('lc_(.*)', os.path.basename(ifile) )
    obj = obj_search.group(1)

    if 'detrended' in obj:
        obj = obj.split('_')[-2]
    
    #    m = sp.in1d(cat.obj_name, sp.uint64(obj) )'    
    print(obj)
    if isinstance(cat.obj_name[0], sp.uint64):
        m = sp.in1d(cat.obj_name, sp.uint64(obj) )
    else:
        m = sp.in1d(cat.obj_name, obj )
    return {'name':cat.obj_name[m][0], 
            'RA':cat.ra[m][0],
            'DEC':cat.dec[m][0]
            }





def get_inputs(args):
    parser = argparse.ArgumentParser( description="Specify TNS light curves to plot---will look up the source in the catalogs and display metadata.")
    parser.add_argument('infiles', nargs='+')
    return parser.parse_args()
    
def main():
    args = get_inputs(sys.argv[1:])
    if len(args.infiles) == 1:
        if args.infiles[0] == 'lc_*':
            print('no input files, exiting')
            sys.exit()

    #don't get rid of any loaded catalogs, or else code is slow
    loaded_cats = {}

    for ifile in args.infiles:
        print(ifile)
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
        print metadata

if __name__== '__main__':
    main()

