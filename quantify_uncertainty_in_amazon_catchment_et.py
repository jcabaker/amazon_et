#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quantify uncertainty in Amazon catchment-mean ET

"""
import iris
import math
from math import pi
import numpy as np
import pandas as pd
import glob
from datetime import datetime
import matplotlib.pyplot as plt
from netCDF4 import Dataset as NetCDFFile
from pyhdf.SD import SD, SDC
from jpros import extract
from jpros import harmonise
from jpros.cube_funcs import get_lons, get_lats


def get_pixel_size(lon):
    res = 360/len(lon)
    lat = np.arange((len(lon)/2)+1)*res-90
    r=6.371*1e6         
    rad=(2*pi/360)               # (m)
    da = np.nan * np.zeros((len(lat)-1))      # (m2)
    
    for i in range(len(lat)-1):
        da[i] = 2*pi*(1/len(lon))*r**2*(math.sin(rad*lat[i+1])-math.sin(rad*lat[i]))
    return(da)


def get_1D_data_for_basin(mask, data):
    masked_data = np.ma.array(data, mask=~mask)
    temp = masked_data[masked_data.mask == False]
    out = temp.data
    return(out)
    
    
#%%

basins = ['amazon_obidos_dissolved']
monthly_ET_errors = []
results = {}

# Read in ET and component data calculated using catchment-balance method
fpath = '/nfs/a68/gyjcab/datasets/et_analysis/'
catchment_et = np.load(fpath+ 'all_basin_catchment_et_2002_2019_jpl_mascon_chirps_hires.npy',
                       allow_pickle=True).item()
startyr = 2003
endyr = 2019
time_constraint = iris.Constraint(time=lambda cell:
                             startyr <= cell.point.year <= endyr)

# Load CHIRPS data
path = ('/nfs/a68/gyjcab/datasets/lapse_data_harmonised/Jan_2018/Final/')
pre = iris.load_cube(path+'1.0deg/pr*chirps*1.0*1981_2020.nc', constraint=time_constraint)
pre.convert_units('kg m^-2 month^-1')

pre_lon = get_lons(pre)
pre_lat = get_lats(pre)

# Calculate area of grid box areas (m2) on globe       
pixel_size_grid = get_pixel_size(pre_lon)
pixel_size_grid = np.array([pixel_size_grid]*len(pre_lon)).transpose()

for basin in basins:
    
    # Read basin catchment data and trim to date range
    basin_name = basin.split('_', 1)[0]
    print(basin_name)
    data = catchment_et[basin_name]
    datemin = datetime(2003, 1, 1, 0, 0)
    datemax = datetime(2019, 12, 31, 0, 0)
    idx = pd.date_range(datemin, datemax, freq='MS')
    data = data.reindex(idx, fill_value=np.nan)
    print(data.head(5))
    print(data.tail(5))
    data.ET.iloc[np.where(data.ET < 0)] = np.nan
    startyr = data.index[0].year
    endyr = data.index[-1].year
    nyear = endyr - startyr + 1
    
    # --------------- Read in basin information
    pre_mask = extract.get_mask(pre_lat, pre_lon, basin)
    
    # Error in dS/dt
    # Use error values from Wiese et al (2016) for Amazon

    sigma_merr = 6.1  # GRACE measurement error
    sigma_lerr = 0.9  # residual leakage error after applying CRI filter and
                      # and gain factors from CLM model

    ## Combine errors in quadrature
    sigma_S = math.sqrt((sigma_merr)**2+(sigma_lerr)**2)

    # Convert to sigma_dSdt
    sigma_dSdt = (sigma_S * math.sqrt(2))
    print(sigma_dSdt)

    # Calculate errors in P
    sigma_P = np.nan *np.zeros((nyear*12))
    Nt = nyear*12
    P_basin = np.nan * np.zeros((Nt))

    for nt in range(Nt):

        # Get finite set of precipitation estimates over basin
        E = get_1D_data_for_basin(pre_mask, pre.data[nt, :, :])

        # Calculate area-weighted precip mean
        masked_data = np.ma.array(pre.data[nt, :, :], mask=~pre_mask)
        masked_weights = np.ma.array(pixel_size_grid, mask=~pre_mask)
        P_basin[nt] = np.ma.average(masked_data, weights=masked_weights)

        # Calculate random error according to Huffman (1997)
        #
        #  sigma_r = rbar ̄* [(H - p)/pN]**(1/2)
        #
        rbar = np.nanmean(E)
        H = 1.5  # constant, Huffman 1997 ref
        i = np.where(E != 0)  # where E is finite set of precip estimates
        p = len(i[0])  # frequency of non zero precipitation in E
        j = np.where(E == E)
        N = len(j[0])  # Number of independent samples in E

        # Combine errors in quadrature to get sigma P
        sigma_random = math.sqrt(abs(rbar*((H - p)/(p*N))))
        P_bias = 0.036  # from Paredes-Trejo et al 2017
        sigma_systematic = P_bias * P_basin[nt]
        sigma_P[nt] = math.sqrt((sigma_random)**2+(sigma_systematic)**2)

    # Combine errors in each of the parameters (all units mm month-1)
    sigma_ET = np.nan* np.zeros((len(data.ET)))  
    sigma_names = ['sigma_P', 'sigma_R', 'sigma_dSdt']
    sigma_R_vals = []
    
    for n in range(len(data.ET)):
        if data.ET[n] == data.ET[n]:
            sigma_R = 0.05*(data.R[n])
            sigma_R_vals.append(sigma_R)
            
            error = math.sqrt(sigma_P[n]**2 + (sigma_R)**2 + sigma_dSdt**2)
            sigma_ET[n] = error

        else:
            sigma_R_vals.append(0.05*(data.R[n]))
            continue
        
    df = pd.DataFrame()
    df['sigma_P'] = sigma_P
    df['sigma_R'] = sigma_R_vals
    df['sigma_dSdt'] = sigma_dSdt
    df['sigma_ET'] = sigma_ET
    df['ET_estimate'] = [x for x in data.ET]
    df['relative_error_ET'] = (df['sigma_ET']/df['ET_estimate'])*100  
    print(df.head())
    print(df.mean())
    print('Min error (%)= ', df['relative_error_ET'].min())
    print('Max error (%)= ', df['relative_error_ET'].max())
    print('Mean error (%)= ', df['relative_error_ET'].mean())
    print('Standard deviation (%)', df['relative_error_ET'].std())
    print('Median error (%) = ', np.nanmedian(df['relative_error_ET']))

    # save data
    outpath = fpath
    outname = basin.split('_', 1)[0] + '_ET_error.csv'
    df.to_csv(outpath+outname)
 
    # Calculate seasonal error
    df['dates'] = data.index
    df = df.set_index('dates')
    seasonal_df = df.groupby([lambda x: x.month]).agg('mean')
    seasonal_df['relative_error_ET']
    print(seasonal_df)
    

