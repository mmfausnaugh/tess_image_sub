import scipy as sp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import spiceypy as s
from datetime import datetime


import poc.configdb as cdb
from poc.poctime import poctime

tjd2utc = poctime('TJD->UTC').convert
utc2tjd = poctime('UTC->TJD').convert
s.boddef("TESS", -95)
cdb.spice.load()


def write_to_file(fout, time_in, tess_position):
    for ii,row in enumerate(tess_position):
        fout.write('{:15.6f} {:15e} {:15e} {:15e} {:8.4f} {:8.4f} {:8.4f}\n'.format(time_in[ii], row[0],row[1],row[2],row[3],row[4],row[5]))


if not os.path.isfile('tess_ephem.txt'):
    t0 = 1250.00080076  #TJD of launch + 23 days, to make spice happy
else:
    t = sp.genfromtxt('tess_ephem.txt',usecols=(0))
    t0 = t[-1]

d = datetime.utcnow()
utc_t1 = d.strftime('%Y-%m-%d-%H:%M:%S')
t1 = utc2tjd(utc_t1)

time_in = sp.r_[t0:t1:0.010412]
utc = tjd2utc(time_in)
t_spiceypy = s.str2et(utc)

#s.spkezr returns 6-element array of position and velocity and a scalar light travel time
tess_position = sp.array([s.spkezr('TESS', tm, 'J2000', 'NONE', '0')[0] for tm in t_spiceypy ])

if not os.path.isfile('tess_ephem.txt'):
    with open('tess_ephem.txt','w') as fout:
        write_to_file(fout, time_in, tess_position)
else:
    with open('tess_ephem.txt','a') as fout:
        write_to_file(fout, time_in, tess_position)
