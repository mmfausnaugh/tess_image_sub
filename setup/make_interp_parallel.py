# Make slice directories with the corresponding dates file
## Input arguments for the script
## $1 - number of processing units to use

import numpy as np
import os
import sys

NPROC = int(sys.argv[1])

fnames = np.genfromtxt('dates',usecols=(0),dtype=str)
tjd    = np.genfromtxt('dates',usecols=(1))

NPERSUB = int(len(fnames)/NPROC) + 1

for ii in range(NPROC):
    min_idx = ii*NPERSUB
    max_idx = (ii + 1)*NPERSUB
    if max_idx >= len(fnames):
        max_idx = len(fnames) 

    # create slice directory if it doesn't exist
    if not os.path.exists('./slice{:03d}'.format(ii)):
        os.mkdir('./slice{:03d}'.format(ii))

    # slice the dates file
    with open('./slice{:03d}/dates'.format(ii),'w') as fout:
        for jj in range(min_idx, max_idx):
            fout.write('{} {:.12f}\n'.format(fnames[jj],tjd[jj]) )

