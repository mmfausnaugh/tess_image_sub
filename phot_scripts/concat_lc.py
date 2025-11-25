#!/usr/bin/env python

import numpy as np
from multiprocessing import Pool
import glob
import os
import sys

duse = os.environ['DATA_DIR']
dhome = os.getcwd()



sector = sys.argv[1]
sectoruse = 's{:04d}'.format(int(sector))
print(sectoruse)

cam = sys.argv[2]
ccd = sys.argv[3]


dout = os.path.join(dhome,
                    "sector"+str(sector),
                    "cam"+str(cam)+"_ccd"+str(ccd)
)

dtarget = os.path.join(duse,
                       sectoruse,
                       "cam"+str(cam)+"-ccd"+str(ccd),
                       )

print(dout)
if os.path.isdir(os.path.join(dout, 'lc')):
    pass
else:
    os.makedirs(os.path.join(dout, 'lc'))

if os.path.isdir(os.path.join(dout, 'bkg_phot','lc')):
    pass
else:
    os.makedirs(os.path.join(dout, 'bkg_phot', 'lc'))
    

    
indirs = glob.glob( os.path.join(
    dtarget, "o*", "slice*"
))
indirs.sort()


def read_data(indir):
    infiles = glob.glob( os.path.join(
        indir,
        "lc/lc_*"
        ))
    infiles.sort()
    output = {}
    for infile in infiles:
        #print(infile)
        d = np.genfromtxt(infile)
        output[ os.path.basename(infile) ] = d

    infiles = glob.glob( os.path.join(
        indir,
        "bkg_phot/lc/lc_*"
        ))
    infiles.sort()
    output_bkg = {}
    for infile in infiles:
        #print(infile)
        d = np.genfromtxt(infile)
        output_bkg[ os.path.basename(infile) ] = d

    return output, output_bkg

def delete_data(indir):
    infiles = glob.glob( os.path.join(
        indir,
        "lc/lc_*"
        ))
    infiles.sort()
    for infile in infiles:

        os.remove(infile)

    infiles = glob.glob( os.path.join(
        indir,
        "bkg_phot/lc/lc_*"
        ))
    infiles.sort()

    for infile in infiles:
        os.remove(infile)
    return 0

results = []
results_bkg = []
for indir in indirs:
    #print(indir)
    out1, out2 = read_data(indir)
    results.append( out1  )
    results_bkg.append( out2 )
    
for lc in results[0].keys():
    print(lc)
    output = []
    output_bkg = []
    
    for ii,r in enumerate(results):
        #print(ii,r)
        try:
            print(indirs[ii], lc)
            output.append( r[lc] )
            output_bkg.append( results_bkg[ii][lc] )
        except KeyError:
            print('error!',indirs[ii], lc)
            #print(os.getcwd())
            #print(lc)
            raise

    output = np.vstack(output)
    output_bkg = np.vstack(output_bkg)

    idx = np.argsort(output[:,0])
    output = output[idx]
    idx = np.argsort(output_bkg[:,0])
    output_bkg = output_bkg[idx]
    
    output = np.unique(output, axis=0)
    output_bkg = np.unique(output_bkg, axis=0)

    
    output_file = os.path.join(dhome,
                               "sector"+str(sector),
                               "cam"+str(cam)+"_ccd"+str(ccd),
                               "lc",
                               os.path.basename(lc)
    )

    np.savetxt(output_file, output)

    output_file2 = os.path.join(dhome,
                                "sector"+str(sector),
                                "cam"+str(cam)+"_ccd"+str(ccd),
                                "bkg_phot",
                                "lc",
                                os.path.basename(lc)
    )
    np.savetxt(output_file2, output_bkg)

    
##for indir in indirs:
    #print(indir)
##    delete_data(indir)
    
