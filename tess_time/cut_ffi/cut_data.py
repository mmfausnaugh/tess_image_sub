import numpy as np
import scipy as sp
import sys
import os
sys.path.insert(0, os.path.abspath(   os.path.dirname(__file__)))

import saturation_times as sat_times

sat_dict = {
    'cam1':sat_times.cam1,
    'cam2':sat_times.cam2,
    'cam3':sat_times.cam3,
    'cam4':sat_times.cam4,
}


def cut_date_range(times,x,y,z):
    m = (x > times[0]) & (x < times[1])
    return x[~m], y[~m], z[~m]

def cut_multisector_data(x,y,z):
    s4_time_cut = [1421.209, 1424.4]
    s8_time_cut = [1534.96096279, 1536.33596279]
    x,y,z = cut_date_range(s4_time_cut, x, y, z)
    x,y,z = cut_date_range(s8_time_cut, x, y, z)

    for ccd in ['ccd1','ccd2','ccd3','ccd4']:
        for sector in sat_dict['cam4'].keys():
            t_ranges = sat_dict['cam4'][sector][ccd]
            for ii in range(len(t_ranges)):
                x,y,z = cut_date_range(t_ranges[ii], x,y,z)
        
    tjd_cut = sp.genfromtxt('/pdo/users/faus/image_sub/pipeline/tess_time/cut_ffi/cut_fin_data',usecols=(2))
    m = []
    for ii,epoch in enumerate(x):
        if any(sp.isclose(tjd_cut,epoch, atol=1.e-4)):
            m.append(ii)
    return sp.delete(x,m), sp.delete(y,m), sp.delete(z,m) 

def cut_data(x,y,z, sector, cam, ccd, bad_cal_times = None):
    s4_time_cut = [1421.209, 1424.4]
    s8_time_cut = [1534.96096279, 1536.33596279]
    x,y,z = cut_date_range(s4_time_cut, x, y, z)
    x,y,z = cut_date_range(s8_time_cut, x, y, z)

    if sector in sat_dict[cam].keys():
        t_ranges = sat_dict[cam][sector][ccd]
        for ii in range(len(t_ranges)):
            x,y,z = cut_date_range(t_ranges[ii], x,y,z)
        
    tjd_cut = sp.genfromtxt('/pdo/users/faus/image_sub/pipeline/tess_time/cut_ffi/cut_fin_data',usecols=(2))
    m = []
    for ii,epoch in enumerate(x):
        if any(sp.isclose(tjd_cut,epoch, atol=1.e-4)):
            m.append(ii)
        if bad_cal_times is not None:
            if any(sp.isclose(bad_cal_times, epoch, atol=1.e-4)):
                m.append(ii)

    m = list(np.unique(m))
    return sp.delete(x,m), sp.delete(y,m), sp.delete(z,m) 


def bad_calibration2TJD(lc_file):
    #assumes that bad_calibration.txt and dates are in the directory
    #above the lc_file
    
    dstem = os.path.dirname(os.path.abspath(lc_file))
    
    if os.path.isfile( os.path.join(dstem, '../bad_calibration.txt')):
        bad_cal = np.genfromtxt(os.path.join(dstem, '../bad_calibration.txt')  )

        times  = np.genfromtxt( os.path.join( dstem, '../dates')  ,usecols=(1))
        fnames = np.genfromtxt( os.path.join( dstem, '../dates')  ,usecols=(0),dtype=str)
        fnums  = np.array([ e.split('-')[1] for e in fnames ]).astype(int)
        
        m = np.in1d(fnums, bad_cal)
        
        #return times to cut
        return times[m]
    else:
        return None

def get_cut_indices(x):
    #for an input time array, return the array of indexes that are bad
    #and should be cut.

    # use sp.delete(arr,m) to delete the bad data, where arr matches x
    #in size/index
    s4_time_cut = [1421.209, 1424.4]
    m = sp.where( ( x > s4_time_cut[0]) & ( x < s4_time_cut[1]) )[0]
    tjd_cut = sp.genfromtxt('/pdo/users/faus/image_sub/pipeline/tess_time/cut_ffi/cut_fin_data',usecols=(2))
    for ii,epoch in enumerate(x):
        if any(sp.isclose(tjd_cut,epoch, atol=1.e-4)):
            m = sp.r_[m, ii]
    return m
