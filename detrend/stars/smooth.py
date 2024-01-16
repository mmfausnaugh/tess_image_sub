import scipy as sp
import sys
from scipy.ndimage import median_filter

for lc in sys.argv[1:]:
    x,y,z = sp.genfromtxt(lc,unpack=1,usecols=(0,1,2))
    ysmooth = median_filter(y,size=100, mode='reflect')
    sp.savetxt(lc+'_smooth',sp.c_[x,ysmooth,z])
