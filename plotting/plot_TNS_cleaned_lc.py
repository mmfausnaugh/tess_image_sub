#!/usr/bin/env python
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import re
import glob
sys.path.insert(0,'/pdo/users/faus')
from catalog2tess_px.catalogs.TNS import TNS
import argparse

from tools.tools import rebin

cat2pix_dir = '/pdo/users/faus/python/catalog2tess_px/'

def plot_sky(ifile, axuse):
    x,y = np.genfromtxt(ifile,unpack=1,usecols=(0,6))
    wdir = os.path.abspath(os.path.dirname(ifile))
    sector_idx = wdir.find('sector')
    sector     = wdir[sector_idx : sector_idx+8]
    cam_idx = wdir.find('cam')
    cam = wdir[cam_idx : cam_idx+4]
    ccd_idx = wdir.find('ccd')
    ccd = wdir[ccd_idx : ccd_idx+4]

    x,y,_ = cut_data(x,y,np.ones(len(y)),sector,cam,ccd)    

    axuse.plot(x,-y,'r.')


def mask_bkg(time,flux,eflux,bkg):
    #counts, bins = np.histogram(bkg,len(bkg)//10)
    #mode = bins[ counts == counts.max() ]

    abs_res = abs( bkg - np.median(bkg) )
    m = abs_res < 5.0*np.median(abs_res)/0.67449
    return time[m],flux[m],eflux[m]
 

def plot_lc(x,y,z,bkg, axuse):
    x,y,z = mask_bkg(x,y,z,bkg)

    axuse.errorbar(x, y, z,fmt='k.')

def plot_bkg_lc(x,y,z,bkg, bkg_mod, bkg2,axuse):
    x2,y,z = mask_bkg(x,y,z,bkg)
    x2,bkg2,bkg = mask_bkg(x,bkg2,bkg,bkg)

    axuse.plot(x2, bkg, 'r.')
    axuse.plot(x,bkg_mod,'m')

def get_meta_data(ifile):
    wdir  =  os.path.abspath( os.path.dirname(ifile))

    #sector number
    sector_search = re.search('sector(\d\d)',wdir)
    sector = sector_search.group(1)
    cam_search = re.search('cam(\d)',wdir)
    cam = cam_search.group(1)
    ccd_search = re.search('ccd(\d)',wdir)
    ccd = ccd_search.group(1)


    cat = TNS(os.path.join(cat2pix_dir, 'TNS/s{:02d}/sector{}_cam{}_transients.txt'.format(int(sector), str(int(sector)), cam)
                       ),ignore_image_buffer=True)


    obj_search = re.search('lc_(\w*)_cleaned',ifile)
    obj = obj_search.group(1)
    print(obj)
    if 'detrended' in obj:
        obj = obj.split('_')[-2]
    
    print(obj)
    m = np.in1d(cat.obj_name, obj)
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

    if metadata['internal_name'] == 'None':
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
    parser.add_argument('--mag',action='store_true',help='If set, plot mags. Assumes this column exists in LC file')
    parser.add_argument('--show',action='store_true',help='If set, open the pyplot interactive plotting window')
    return parser.parse_args()
    
def main():
    args = get_inputs(sys.argv[1:])
    if len(args.infiles) == 1:
        if args.infiles[0] == 'lc_*':
            print('no files to plot, exiting..')
            sys.exit()

    for ifile in args.infiles:
        print(ifile)
        if 'png' in ifile:
            continue
        #if 'detrend' in ifile:
        #    continue
        if 'cleaned' not in ifile:
            continue
        if os.path.isdir(ifile):
            continue
        if 'lc_*' in ifile:
            continue

        try:
            metadata = get_meta_data(ifile)
        except Exception as e:
            print(e)
            continue

        x,y,z,bkg,bkg_mod,bkg2 = np.genfromtxt(ifile,unpack=1,usecols=(0,2,3,6,7,8),skip_header=1)

        if args.mag:
            mag,emag = np.genfromtxt(ifile,unpack=1,usecols=(4,5),skip_header=1)
            

        if args.SN:
            #check if the prefix is a SN.  If not, move to next in the
            #loop
            if metadata['prefix'] != 'SN':
                continue

        if args.bkg:
            F,(ax1,ax2,ax3) = plt.subplots(3,1, sharex='col')        
        else:
            F,(ax1) = plt.subplots(1,1)     


        if args.mag:
            emask = emag == 99.9            
            plot_lc(x[~emask],
                    mag[~emask],emag[~emask],
                    bkg[~emask], ax1)
            ax1.plot(x[emask], mag[emask],'k^')
            if args.bkg:
                plot_bkg_lc(x,y,z, bkg,bkg_mod,bkg2,ax2)
                #correct fluxes and reconver to mags
                corrected_flux = y - bkg_mod
                mag_cor = np.zeros(len(corrected_flux))
                emag_cor = np.zeros(len(corrected_flux))

                mask = corrected_flux < 3*z
                mag_cor[~mask]  = -2.5*np.log10(corrected_flux[~mask]) + 20.44
                emag_cor[~mask] = z[~mask]/corrected_flux[~mask]*2.5/np.log(10)
                mask2 = mag_cor == 0

                plot_lc(x[~mask2],mag_cor[~mask2], emag_cor[~mask2], bkg[~mask2], ax3)
                

                l,h = ax3.get_ylim()
                ax3.set_ylim([h,l])


                ax3.set_xlabel('BTJD $- 2\,457\,000$')
                ax3.set_ylabel("T mag $-$\nbkg_model")

                ax2.set_ylabel('Bkg (red)/\nbkg_model (purple)')

            l,h = ax1.get_ylim()
            ax1.set_ylim([h,l])

            ax1.set_ylabel("T mag")
            
            

        else:
            plot_lc(x,y,z,bkg,ax1)
            if args.bkg:
                plot_bkg_lc(x,y,z, bkg,bkg_mod,bkg2,ax2)
                plot_lc(x,y - bkg_mod, z, bkg, ax3)

                ax3.set_xlabel('BTJD $- 2\,457\,000$')
                ax3.set_ylabel("T mag $-$ bkg_model")

                ax2.set_ylabel('Bkg (red)/\n bkg_model (purple)')


            ax1.set_ylabel("T mag")

        F.subplots_adjust(hspace=0)

        format_plot(ax1, metadata)


        plt.savefig(os.path.splitext(ifile)[0]+'.png' )     
        plt.close()
    if args.show:
        plt.show()

if __name__== '__main__':
    main()

