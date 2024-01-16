import numpy as np
import matplotlib.pyplot as plt
import os

cutlist = np.genfromtxt('cut_ffi_list')
cutlist = cutlist.astype(int)

finout = []
tout = []
sout = []
for i in range(100):
    if os.path.isfile('s{}_dates'.format(i+1)):
        fnames = np.genfromtxt('s{}_dates'.format(i+1),usecols=(0),dtype=str)
        tjd = np.genfromtxt('s{}_dates'.format(i+1),usecols=(1))

        fin = np.array([int(f.split('-')[1]) for f in fnames  ])

        m = np.in1d(fin, cutlist)
        finout = np.r_[finout, fin[m]]
        tout = np.r_[tout, tjd[m]]
        sout = np.r_[sout, [i+1]*len(np.where(m)[0])]

np.savetxt('cut_fin_data',np.c_[sout,finout,tout],fmt='%i %i %.8f')
