#!/usr/bin/env python
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
from astropy.io import fits

import os
import sys
import glob
import re
sys.path.insert(0,'/pdo/users/faus')
from catalog2tess_px.catalogs.HyperLedaCsv import HyperLedaCsv
import argparse
from tess_time.cut_ffi.cut_data import cut_data

def get_meta_data(ifile):
#    wdir  =  os.path.abspath( os.path.dirname(ifile))


    #sector number
    sector_search = re.search('sector(\d\d)',ifile)
    sector = sector_search.group(1)
    cam_search = re.search('cam(\d)',ifile)
    cam = cam_search.group(1)
    ccd_search = re.search('ccd(\d)',ifile)
    ccd = ccd_search.group(1)
                               

    cat = HyperLedaCsv('/pdo/users/faus/python/catalog2tess_px/HyperLEDA/s{:02d}/hyperleda_s{:02d}_cam{}.txt'.format(int(sector), int(sector), cam))

    obj = ifile.split('_')[-2]
    print(obj)
    m = np.in1d(cat.obj_name, obj)
    return {'obj':obj,
            'imag':cat.imag[m][0], 
            'sector':sector,
            'cam':cam,
            'ccd':ccd,
            }

def plot_sky(x,y,z,bkg,bkg_mod, axuse_mid, axuse_lower,imag):

    axuse_mid.plot(x,bkg,'r.')
    axuse_mid.plot(x,bkg_mod,'m')
    #pretend that Tmag == imag
    cts = 10**(-0.4*(imag - 20.44))
    #this time, subtract bkg_mod from y)
    flux = cts + (y - bkg_mod)/1800/0.8/0.99
    eflux = z/1800/0.8/0.99
    m = flux < 0
    flux[m] = 2.9*eflux[m]

    mag = -2.5*np.log10(flux) + 20.44
    m1 = flux < 3*eflux
    mag[m1] = -2.5*np.log10(3*eflux[m1]) + 20.44

    emag = eflux/flux*2.5/np.log(10)
    m2 = emag < 0.3
    axuse_lower.errorbar(x[m2],mag[m2],emag[m2],fmt='k.')
    axuse_lower.plot(x[m1],mag[m1],'k^')

    l,u = axuse_lower.get_ylim()
    axuse_lower.set_ylim([u,l])


    axuse_lower.set_ylabel('mag')
    axuse_lower.set_xlabel('TJD (days)')

    axuse_mid.set_ylabel('bkg flux')

def plot_lc(x,y,z, axuse, imag):
    #pretend that Tmag == imag
    cts = 10**(-0.4*(imag - 20.44))
    flux = cts + y/1800/0.8/0.99
    eflux = z/1800/0.8/0.99
    m = flux < 0
    flux[m] = 2.9*eflux[m]

    m = flux >0
    x,flux,eflux = x[m], flux[m], eflux[m]

    m1 = flux < 3*eflux
    mag = -2.5*np.log10(flux) + 20.44
    mag[m1] = -2.5*np.log10(3*eflux[m1]) + 20.44

    emag = eflux/flux*2.5/np.log(10)
    m2 = emag < 0.3
    axuse.errorbar(x[m2], mag[m2], emag[m2], fmt='k.')
    axuse.plot(x[m1],mag[m1],'k^')

    l,u = axuse.get_ylim()
    axuse.set_ylim([u,l])

    axuse.set_ylabel('mag')
    axuse.set_xlabel('TJD (days)')



def format_plot(axuse,obj, h_class, m_class, imag, sector, cam, ccd ):

    title = '{} hyperLeda={} milliquas={} Imag={}'.format(
        obj, h_class, m_class, imag,)

    axuse.set_title(title,fontsize='x-large')


    h,l = axuse.get_ylim()
    l2,h2 = axuse.get_xlim()
    c1 = l2 + (h2-l2)*0.05
    c2 = l  + (h - l)*0.9
    axuse.text(c1,
               c2,
               's{} cam{}ccd{}'.format(sector,
                                       cam,ccd),
               fontsize='large')
    
def get_inputs(args):
    parser = argparse.ArgumentParser( description="Specify Gaia var star light curves to plot---will look up the source in the catalogs and display metadata.")
    parser.add_argument('infiles', nargs='+')
    return parser.parse_args()
    
def main():
    args = get_inputs(sys.argv[1:])

    for ifile in args.infiles:
        #first load the file
        ifile = os.path.abspath(ifile)
        print(ifile)


        #sector number
        sector_search = re.search('sector(\d\d)',ifile)
        sector = sector_search.group(1)
        cam_search = re.search('cam(\d)',ifile)
        cam = cam_search.group(1)
        ccd_search = re.search('ccd(\d)',ifile)
        ccd = ccd_search.group(1)

        obj_search = re.search('lc_(\w.+)_cleaned',ifile)
        obj = obj_search.group(1)
        if 'lc' in obj:
            print(obj)
            obj_search = re.search('lc_(\w.+)',obj)
            obj = obj_search.group(1)
            
 
        #find the light curve
        dstem = '/data/tess/image_sub/sector{}/cam{}_ccd{}/'.format(sector,cam,ccd)
        #dstem= './'

        #try:
        #    meta_data = get_meta_data(ifile)
        #except:
        #    continue
        #pbj=
        #obj = meta_data['obj']
        #imag = meta_data['imag']
        imag = 10
        #print(obj, imag)
        outfile = os.path.join('lc_{}_sector{}_cam{}_ccd{}.png'.format(obj,sector,
                                                                       cam,ccd))
        print(outfile)
        if os.path.isfile(outfile):
            continue


        ref_file = os.path.join(dstem, 'ref.fits')
        rms_file = os.path.join(dstem, 'rms.fits')
        print(os.path.dirname(ifile))
        #phot_file = os.path.join(os.path.dirname(os.path.dirname(ifile)),'phot.data')
        phot_file = os.path.join(os.path.dirname(ifile),'phot.data')


        ref_image = fits.getdata(ref_file)
        rms_image = fits.getdata(rms_file)
        #get coords, plot up ref and rms image
        phot_data = np.genfromtxt(phot_file, dtype=str)
        #phot_data = np.genfromtxt(ifile, dtype=str)
        print(phot_data, phot_data.ndim)
        if phot_data.ndim == 1:
            names = phot_data[4].replace('lc/','') 
        else:
            names = np.array([lc.replace('lc/','') for lc in phot_data[:,4] ])
        #print(phot_file)

        if os.path.isfile(outfile):
            continue
        #fuse = os.path.join(dstem,
        #                    'lc_hyperleda/lc_{}_cleaned'.format(obj) )
        fuse = os.path.join(ifile)

        try:
            #old style
            #x,y,z, bkg, bkg_mod = np.genfromtxt(fuse,unpack=1,usecols=(0,2,3,4,5),skip_header=1)
            x,y,z, bkg, bkg_mod = np.genfromtxt(fuse,unpack=1,usecols=(0,2,3,6,7),skip_header=1)
            abs_res = abs(bkg - np.median(bkg))
            m = abs_res < 5*np.median(abs_res)/0.67449
            x,y,z,bkg,bkg_mod = x[m],y[m],z[m],bkg[m],bkg_mod[m]


        except Exception as e:
            print(e)
            continue
            

        F = plt.figure()
        gs1 = gridspec.GridSpec(6,8)
        ax1 = F.add_subplot( gs1[0:2,0:6] )
        ax2 = F.add_subplot( gs1[2:4,0:6] )
        ax3 = F.add_subplot( gs1[4:, 0:6] )

        #ref image
        ax4 = F.add_subplot( gs1[0:3,6:] )
        #rms image                       
        ax5 = F.add_subplot( gs1[3:,6:] )

        plot_lc(x,y,z, ax1, imag)

        plot_sky(x,y,z,bkg,bkg_mod, ax2, ax3, imag)

        format_plot(ax1,obj, '', 
                    '', 
                    imag, 
                    sector, cam, ccd )



        print('tmp',names, 'lc_'+obj, obj)
        lookup_file = np.in1d(names, 'lc_' + obj )
        if phot_data.ndim == 1:
            col,row, col_px,row_px = phot_data[ [0,1,2,3] ]
        else:
            print('check lookup',lookup_file, phot_data[lookup_file])
            col,row, col_px,row_px = phot_data[lookup_file][0][ [0,1,2,3] ]
        #print(col,col_px)
        col = float(col)
        row = float(row)
        col_px = int(col_px)
        row_px = int(row_px)
        #print(col,col_px, col-col_px + 5)

        col_idx = slice( col_px - 5, col_px + 6,1)
        row_idx = slice( row_px - 5, row_px + 6,1)

        ax1.set_xticklabels([])
        ax2.set_xticklabels([])
        vl,vh = np.percentile( np.ravel(ref_image[row_idx, col_idx]),[10,90])
        ax4.imshow(ref_image[row_idx, col_idx],origin='lower',
                   vmin = vl, vmax = vh )
        ax4.plot(col - col_px + 5,
                 row - row_px + 5,'bo')
        ax4.set_title('ref')

        
        vl,vh = np.percentile( np.ravel(rms_image[row_idx, col_idx]),[10,90])
        ax5.imshow(rms_image[row_idx, col_idx],origin='lower',
                   vmin = vl, vmax = vh )
        ax5.plot(col - col_px + 5,
                 row - row_px + 5,'bo')
        ax5.set_title('rms')



        plt.subplots_adjust(hspace=0, wspace=0)
        F.set_size_inches(8,6)
        plt.savefig(outfile)                
                
        plt.close()
        fits.writeto('ref_{}.fits'.format(obj),ref_image[row_idx, col_idx])
        fits.writeto('rms_{}.fits'.format(obj),rms_image[row_idx, col_idx])

#            if args.show:
#                plt.show()

if __name__== '__main__':
    main()

#for i in 1 3; do for  j in 1 2 3 4; do cd cam${i}_ccd${j}; pwd; for d in discovery postdiscovery prediscovery; do cp lc_${d}/phot.data . ; mkdir lc; python ~/image_sub/ap_phot.py; mv lc/ref.phot lc_${d}/ref.phot; done ; cd ..; done; done
