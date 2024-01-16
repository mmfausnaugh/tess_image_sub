import scipy as sp
import matplotlib.pyplot as plt
import scipy as sp
import matplotlib.pyplot as plt
import sys
import os
from scipy import linalg
from scipy.ndimage import median_filter
import argparse


def linfit(x,y,ey):
    """
    This function minimizes chi^2 for a least squares fit to a simple
    linear model.  The errors in x are assumed to be much smaller than
    the errors in y.  It automatically fills in the Fisher matrix, and
    solves the simultaneous equations.

    The function returns p, and covar.  p[0] is the zeropoint
    p[1] is the slope.


    you must take the square root to get the errors, in all cases.
    """                                                                                  
    C = sp.array([sp.sum(y/ey/ey),sp.sum(y*x/ey/ey)])
    A = sp.array([
            [sp.sum(1./ey/ey), sp.sum(x/ey/ey)],
            [sp.sum(x/ey/ey),  sp.sum(x*x/ey/ey)]
            ] )
    p     = linalg.solve(A,C)
    covar = linalg.inv(A)
    return p,covar   


dstem  = '/pdo/users/faus/image_sub/sector4/cam4_ccd2/lc_postdiscovery/'

x0,f,ef = sp.genfromtxt(dstem + 'lc_2018hkx',unpack=1,usecols=(0,1,2))
data = sp.genfromtxt(dstem + 'lc_2018hkx')

tfit = [1413.36, 1416.2]
m = (x0 > tfit[0]) & (x0 < tfit[1])

#linear model seems the most sensible, since either the correction
#isn't constant over time, or is already consistent with a parabola
p,covar = linfit(x0[m], f[m], sp.ones(len(f[m])))
#p = sp.polyfit(x0[m], f[m], 2)
print(p)


talign = [1410.9, 1413.25]
m = (x0 > talign[0]) & (x0 < talign[1])
predict = x0[m]*p[1] + p[0]
#predict = x0[m]**2*p[0] + x0[m]*p[1] + p[2]

shift0 = sp.mean(predict - f[m])
print shift0

scale0 = sp.sum(f[m]*predict)/sp.sum(f[m]**2)

plt.plot(x0,-f,'k.')
plotx = sp.r_[talign[0]:tfit[1]:100j]
ploty = p[1]*plotx + p[0]
#ploty = p[0]*plotx**2 + p[1]*plotx + p[2]

plt.plot(x0[m], -(f[m] + shift0),'m.')
plt.plot(x0[m], -(f[m]*scale0),'r.')
plt.plot(plotx,-ploty,'r',zorder=2)

data[:,1][m] = f[m] + shift0

sp.savetxt(dstem + 'lc_pointing_correct_2018hkx', data,fmt='%f')

plt.show()
