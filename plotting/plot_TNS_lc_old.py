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
    print('check')
    print(obj)

    
    m = sp.in1d(cat.obj_name, obj)
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
            }

def plot_sky(ifile, axuse):
    print 'in sky!'
    x,y = sp.genfromtxt(ifile,unpack=1,usecols=(0,6))
    axuse.plot(x,-y,'r.')


def plot_lc(ifile, axuse, fluxcal=None, plot_mag=False):
    x,y,z = sp.genfromtxt(ifile,unpack=1,usecols=(0,1,2))

    x,y,z = cut_data(x,y,z)
    
    if fluxcal is not None:

        #assume photometry file is in directory with light curve
        targets = sp.genfromtxt(fluxcal,usecols=(1),dtype=str)
        cts = sp.genfromtxt(fluxcal,usecols=(5))

    
        m = sp.in1d(targets,ifile.split('_')[-1])

        flux = (cts[m] - y)/(1800.0*0.8)
        eflux = z/(1800*0.8)
        m2 = flux > 0

        mag = -2.5*sp.log10(flux[m2]/15000.0) + 10
        emag = eflux[m2]/flux[m2]*2.5/sp.log(10)


        if plot_mag:
            m3 = emag < 0.8

            axuse.errorbar(x[m2][m3],mag[m3], emag[m3], fmt='k.')            
            l,u = axuse.get_ylim()
            if l < u:
                axuse.set_ylim([u,l])

            l,u = axuse.get_ylim()
            if mag[m3].max() > l:
                l = mag[m3].max()
            if mag[m3].min() < u:
                u = mag[m3].min()
            axuse.set_ylim([l,u])


            axuse.set_ylabel('Tmag')
        else:
            axuse.errorbar(x, flux, eflux, fmt='k.')
            l,u = axuse.get_ylim()
            if flux.min() < l:
                l = flux.min()
            if flux.max() > u:
                u = flux.max()
            axuse.set_ylim([l,u])

            axuse.set_ylabel('electrons/s')
        axuse.set_xlabel('TJD (days)')
    else:
        axuse.errorbar(x, - y, z,fmt='k.')

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
    parser.add_argument('--fluxcal',default=None, help='If set, specifies the file to read reference fluxes and reports light curves in magnitudes')
    parser.add_argument('--mag',action='store_true',help='If set, plot in magnitudes instead of flux')
    parser.add_argument('--SN',action='store_true',help='If set, only plot confirmed SNe in TNS')
    parser.add_argument('infiles', nargs='+')
    parser.add_argument('--bkg',action='store_true',help='If set, also plot the background estimate')
    parser.add_argument('--combine',action='store_true',help='If set, look in ~faus/image_sub for the same lc file name in other sectors, and plot everything')
    parser.add_argument('--show',action='store_true',help='If set, open the pyplot interactive plotting window')
    return parser.parse_args()
    
def main():
    args = get_inputs(sys.argv[1:])

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
        plot_lc(ifile, ax1, fluxcal=args.fluxcal, plot_mag=args.mag)
        format_plot(ax1, metadata)

        if args.bkg:
            plot_sky(ifile, ax1)

        if args.combine:
            dirstem = '/pdo/users/faus/image_sub/'
            for sector  in range(13):
                if os.path.isdir(os.path.join(dirstem,'sector{}'.format(sector+1))):
                    for lcfile in glob.glob(os.path.join(dirstem,
                                                         'sector{}'.format(sector+1),
                                                         '*',
                                                         'lc*',
                                                         'lc_*')):
                        
                        if 'png' in lcfile:
                            continue
                        if os.path.basename(ifile) in lcfile:
                            if os.path.abspath(ifile) == os.path.abspath(lcfile):
                                continue
                            print ifile, lcfile
                            
                            try:
                                if args.fluxcal is not None:
                                    plot_lc(lcfile, ax1, fluxcal='sector{}/coa_phot.txt'.format(sector+1), plot_mag=args.mag)
                                else:
                                    plot_lc(lcfile, ax1)
                            except:
                                continue
        plt.savefig(os.path.splitext(ifile)[0]+'.png',fmt='png' )                
        
    if args.show:
        plt.show()

if __name__== '__main__':
    main()

#for i in 1 3; do for  j in 1 2 3 4; do cd cam${i}_ccd${j}; pwd; for d in discovery postdiscovery prediscovery; do cp lc_${d}/phot.data . ; mkdir lc; python ~/image_sub/ap_phot.py; mv lc/ref.phot lc_${d}/ref.phot; done ; cd ..; done; done
