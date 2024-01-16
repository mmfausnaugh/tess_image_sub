#!/usr/bin/env python
import scipy as sp
import matplotlib.pyplot as plt
import os
import sys
import re
import glob
sys.path.insert(0,'/pdo/users/faus')
from catalog2tess_px.catalogs.TNS import TNS
import argparse
from tess_time.cut_ffi.cut_data import cut_data


def plot_sky(ifile, axuse):
    x,y = sp.genfromtxt(ifile,unpack=1,usecols=(0,6))
    wdir = os.path.abspath(os.path.dirname(ifile))
    sector_idx = wdir.find('sector')
    sector     = wdir[sector_idx : sector_idx+8]
    cam_idx = wdir.find('cam')
    cam = wdir[cam_idx : cam_idx+4]
    ccd_idx = wdir.find('ccd')
    ccd = wdir[ccd_idx : ccd_idx+4]

    x,y,_ = cut_data(x,y,sp.ones(len(y)),sector,cam,ccd)    

    axuse.plot(x,-y,'r.')


def plot_lc(ifile, axuse):
    x,y,z = sp.genfromtxt(ifile,unpack=1,usecols=(0,1,2))
    wdir = os.path.abspath(os.path.dirname(ifile))
    sector_idx = wdir.find('sector')
    sector     = wdir[sector_idx : sector_idx+8]
    cam_idx = wdir.find('cam')
    cam = wdir[cam_idx : cam_idx+4]
    ccd_idx = wdir.find('ccd')
    ccd = wdir[ccd_idx : ccd_idx+4]

    x,y,z = cut_data(x,y,z,sector,cam,ccd)    
    axuse.errorbar(x, - y, z,fmt='k.')


def get_meta_data(ifile):
    wdir  =  os.path.abspath( os.path.dirname(ifile))

    #sector number
    sector_search = re.search('sector(\d\d)',wdir)
    sector = sector_search.group(1)
    cam_search = re.search('cam(\d)',wdir)
    cam = cam_search.group(1)
    ccd_search = re.search('ccd(\d)',wdir)
    ccd = ccd_search.group(1)


    cat = TNS('/pdo/users/faus/python/catalog2tess_px/TNS/s{:02d}/sector{}_cam{}_transients.txt'.format(int(sector), str(int(sector)), cam))


    obj_search = re.search('lc_2(\w*)',ifile)
    obj = '2'+obj_search.group(1)

    
    m = sp.in1d(cat.obj_name, obj)
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
            }



def format_plot(axuse,metadata):

    if metadata['internal_name'] is 'None':
        name_use = metadata['group']
    else:
        name_use = metadata['internal_name']

    title = '{}{}  {} \n{}{} {} z= {}'.format(metadata['prefix'], 
                                        metadata['name'],
                                        name_use,
                                        metadata['mag'],
                                        metadata['fband'],
                                        metadata['obj_type'],
                                        metadata['z'])

    axuse.set_title(title,fontsize='x-large')

    l,h = axuse.get_ylim()
    axuse.plot([metadata['tjd'],metadata['tjd']],[l,h],'r--')
    axuse.set_ylim([l,h])

    l2,h2 = axuse.get_xlim()
    c1 = l2 + (h2-l2)*0.05
    c2 = l  + (h - l)*0.9
    axuse.text(c1,
               c2,
               's{} cam{}ccd{}'.format(metadata['sector'],
                                       metadata['cam'],
                                       metadata['ccd']),
               fontsize='large')

def get_inputs(args):
    parser = argparse.ArgumentParser( description="Specify TNS light curves to plot---will look up the source in the catalogs and display metadata.")
    parser.add_argument('--SN',action='store_true',help='If set, only plot confirmed SNe in TNS')
    parser.add_argument('infiles', nargs='+')
    parser.add_argument('--bkg',action='store_true',help='If set, also plot the background estimate')
    parser.add_argument('--show',action='store_true',help='If set, open the pyplot interactive plotting window')
    return parser.parse_args()
    
def main():
    args = get_inputs(sys.argv[1:])
    if len(args.infiles) == 1:
        if args.infiles[0] == 'lc_*':
            print('no data files, exiting...')
            sys.exit()


    for ifile in args.infiles:
        if 'cleaned' in ifile:
            continue
        if 'png' in ifile:
            continue
        try:
            metadata = get_meta_data(ifile)
        except Exception as e:
            print(e)
            continue

        
        if args.SN:
            #check if the prefix is a SN.  If not, move to next in the
            #loop
            if metadata['prefix'] != 'SN':
                continue

        F,(ax1) = plt.subplots(1,1)        
        plot_lc(ifile, ax1)
        format_plot(ax1, metadata)

        if args.bkg:
            plot_sky(ifile, ax1)

        plt.savefig(os.path.splitext(ifile)[0]+'.png',fmt='png' )                
        
    if args.show:
        plt.show()

if __name__== '__main__':
    main()

