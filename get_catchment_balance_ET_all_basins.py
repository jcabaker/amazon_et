#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on  Thursday 14 May 2020

This script calculates ET using a catchment balance approach

Requirements:
    1. Precipitation data
    2. River discharge data
    3. GRACE water storage

@author: earjba
"""

import numpy as np
import iris
import iris.coord_categorisation
import pandas as pd
import time
from datetime import datetime
from jpros import extract
from jpros.cube_funcs import get_lats, get_lons
from math import pi, sin
iris.FUTURE.netcdf_promote = True
iris.FUTURE.netcdf_no_unlimited = True
iris.FUTURE.cell_datetime_objects = True


def substring_before(s, delim):
    return(s.partition(delim)[0])


def get_dates_as_decimals(cube):
    time = cube.coord('time').points
    t_unit_yr = int(str(cube.coord('time').units)[11:15])

    # Get years and days in each year
    yrs = [x.year for x in 
           cube.coord('time').units.num2date(cube.coord('time').points)]
    yr_days = [366 if yr%4 == 0 else 365 for yr in yrs]
    
    # Get time in decimals
    t_yrAD = t_unit_yr+(time/yr_days)
    return(t_yrAD)
    
    
def get_pixel_size(lon):
    res = 360/len(lon)
    lat = np.arange((len(lon)/2)+1)*res-90
    r=6.371*1e6         
    rad=(2*pi/360)               # (m)
    da = np.nan * np.zeros((len(lat)-1))      # (m2)
    
    for i in range(len(lat)-1):
        da[i] = 2*pi*(1/len(lon))*r**2*(sin(rad*lat[i+1])-sin(rad*lat[i]))
    return(da)


def toYearFraction(date):
    def sinceEpoch(date): # returns seconds since epoch
        return time.mktime(date.timetuple())
    s = sinceEpoch

    year = date.year
    startOfThisYear = datetime(year=year, month=1, day=1)
    startOfNextYear = datetime(year=year+1, month=1, day=1)

    yearElapsed = s(date) - s(startOfThisYear)
    yearDuration = s(startOfNextYear) - s(startOfThisYear)
    fraction = yearElapsed/yearDuration

    return(date.year + fraction)

#%%
path = ('/nfs/a68/gyjcab/datasets/lapse_data_harmonised/Jan_2018/Final/')

# Read P data
startyr = 2002
endyr = 2019  # can't do 2019 because GRACE data go weird
constraint = iris.Constraint(time=lambda cell:
                             startyr <= cell.point.year <= endyr)

pre = iris.load_cube(path+'hires_for_IFL/pr_chirps_mon_0.05deg_1981_2020.nc', constraint=constraint)

# Convert P data from mm s-1 to mm month-1
pre.convert_units('kg m^-2 month^-1')

# Only need P data from May 2002
pre = pre[4:, :, :]

# Get lat and lon
pre_lon = pre.coord('longitude').points
pre_lat = pre.coord('latitude').points


# Read in GRACE data
## Use JPL Mascon solution - see email 21 May 2020, units cm
path = '/nfs/a68/gyjcab/datasets/lapse_data_harmonised/Jan_2018/Final/0.5deg/'
grace_jpl = iris.load_cube(path+'lwe*jpl_mascon*2020.nc', constraint=constraint)

grace = grace_jpl
grace_lon = grace.coord('longitude').points
grace_lat = grace.coord('latitude').points
grace_time = grace.coord('time').points
grace_dates = grace.coord('time').units.num2date(grace.coord('time').points)

# Convert grace time coordinates to decimal dates
t_yrAD = get_dates_as_decimals(grace)

# Get pre time coordinates in decimal dates
pr_t_yrAD = get_dates_as_decimals(pre)
#%%
# Basin shapefiles (created by aggregating sub-basin shapefiles in QGIS)

basin_shapes = ['purus_dissolved', 'madeira_dissolved',
                'negro_dissolved',  'xingu_dissolved',
                'jari_dissolved',  'japura_dissolved',
                'branco_dissolved','aripuana_dissolved',
                'solimoes_dissolved5', 'tapajos_dissolved3',
                'amazon_obidos_dissolved']

basin_shapes.sort()

# Read in river data
riv_path = '/nfs/a68/gyjcab/datasets/river_data/downloaded_2020/'

filenames = ['Amazon_flow_data_sorted.csv',
             'Branco_flow_data_sorted.csv',
             'Aripuana_flow_data_sorted.csv',
             'Japura_flow_data_sorted.csv',
             'Jari_flow_data_sorted.csv',
             'Madeira_flow_data_sorted.csv',
             'Negro_flow_data_sorted.csv',
             'Purus_flow_data_sorted.csv',
             'Tapajos_Itaituba_flow_data_sorted.csv',
             'Solimoes_flow_data_sorted.csv',
             'Xingu_flow_data_sorted.csv']

riv_data = {substring_before(fname, '_'): pd.read_csv((riv_path+fname), sep=',') for fname in filenames}

#%%
# Calculate change in water storage with respect to time using
# backward-difference approach (dS_dt)

calc_dsdt = True
if calc_dsdt is True:
    Nt = grace.shape[0]
    dS_dt = np.nan * np.zeros((grace.shape))
    
    # Calculate for all pixels and then average by basin in script below
    for n in range(0, Nt-1): 
        
        # Calculate change in S using backward difference
        dS = grace.data[n+1, :, :] - grace.data[n, :, :]
        
        # Calculate dt in months - i.e. no. days / days in a month
        dt = (grace_time[n+1]-grace_time[n])/30.5  # time in months
        
        dS_dt[n, :, :] = dS/dt  # cm month-1     


# Remove trailing nan
dS_dt = dS_dt[0:-1, :, :]        
print(dS_dt.shape)
print('dS_dt shape', dS_dt.shape)

# Calculate area of grid box areas (m2) on globe       
onedeg_pixel_size_grid = get_pixel_size(grace_lon)
onedeg_pixel_size_grid = np.array([onedeg_pixel_size_grid]*len(grace_lon)).transpose()

pre_pixel_size_grid = get_pixel_size(pre_lon)
pre_pixel_size_grid = np.array([pre_pixel_size_grid]*len(pre_lon)).transpose()
print(pre_pixel_size_grid.shape)

# Calculate ET for Amazon sub-basins 
results_dict = {}
for basin in basin_shapes:
    #print(basin)
    """For each catchment get mask, calc P, R and dS_dt and use to calculate
    catchment ET"""
    areas = {}
    out = {}
    
    basin_name = substring_before(basin, '_')
    
    # Get basin mask
    pre_lat = get_lats(pre)
    pre_lon = get_lons(pre)
    
    pre_mask = extract.get_mask(pre_lat, pre_lon, basin)
    onedeg_mask = extract.get_mask(grace_lat, grace_lon, basin)
    
    # Get area of basin in m2
    area = np.sum(pre_mask*pre_pixel_size_grid)
    areas[basin_name] = area
    print(basin_name + ' basin = ' + str(area) + ' m2')
    
    # First calculate pre over catchment for May 2002 to Dec 2018
    Nt = pre.shape[0]
    P_basin = np.nan * np.zeros((Nt))
    shp_path = '/nfs/a68/gyjcab/datasets/shapefiles/'
    for nt in range(Nt):
        masked_data = np.ma.array(pre.data[nt+0, :, :], mask=~pre_mask) # +9 to get from jan 2003
        masked_weights = np.ma.array(pre_pixel_size_grid, mask=~pre_mask)
        
        # Calculate area-weighted precip mean
        P_basin[nt] = np.ma.average(masked_data, weights=masked_weights)

    # Get days in month over analysis timeframe 
    dates = pre.coord('time').units.num2date(pre.coord('time').points)
    dates = [datetime(date.year, date.month, 1) for date in dates]
    
    month_days = np.nan * np.zeros((len(dates)))
    leap = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    non_leap = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    for i in range(len(dates)):
        date = dates[i]
        year = date.year
        month = date.month
        if year % 4 == 0:
            month_days[i] = leap[month-1]
        else:
            month_days[i] = non_leap[month-1]
    datemin = dates[0]
    datemax = dates[-1]
   
    # Then get river data
    riv_key = substring_before(basin, '_').title()
    if riv_key.lower() != basin.split('_')[0]: 
        print('river data from wrong basin', basin, riv_key)
        assert False
    R_df = riv_data[riv_key].copy()

    # Set dates to index
    new_cols = R_df.columns.values
    new_cols[0] = 'Dates'
    R_df.columns = new_cols
    R_df.Dates = pd.to_datetime(R_df.Dates, format='%Y-%m-%d')
    R_flux = R_df.set_index('Dates')
   
    # Make sure only unique dates in dataframe
    R_flux = R_flux.groupby(R_flux.index).mean()

    # Select data from the right timeframe and insert nan if missing dates
    R_flux = R_flux[datemin:datemax]
    idx = pd.date_range(datemin, datemax, freq='MS')
    R_flux = R_flux.reindex(idx, fill_value=np.nan)
    
    # Convert river data from m3 s-1 to mm month-1
    R_data = R_flux.Media.values*60*60*24*month_days  # First convert to m3 month-1
    R = (R_data/area)*1e3  # Then convert to mm month-1
    
    # Get dS_dt and S average over catchment in cm month-1 using area-weighted averaging
    dSdt_basin = np.nan * np.zeros((grace.shape[0]-1))
    S_basin = np.nan * np.zeros((grace.shape[0]-1))
    for nt in range(grace.shape[0]-1):
        masked_data = np.ma.array(dS_dt[nt, :, :], mask=~onedeg_mask)
        masked_weights = np.ma.array(onedeg_pixel_size_grid, mask=~onedeg_mask)
        dSdt_basin[nt] = np.ma.average(masked_data, weights=masked_weights) 
        
        masked_data = np.ma.array(grace.data[nt, :, :], mask=~onedeg_mask)
        S_basin[nt] = np.ma.average(masked_data, weights=masked_weights) 
    
    
    # Interpolate values of each variable to the same time series
    #x = pr_t_yrAD[9:]
    x = pr_t_yrAD
    y = P_basin
    f_P = interp1d(x, y, kind='linear', fill_value="extrapolate")
    
    R_t_yrAD = [toYearFraction(date) for date in R_flux.index]
    x = R_t_yrAD
    y = R
    f_R = interp1d(x, y, kind='linear', fill_value="extrapolate")
    
    tm = 0.5*(t_yrAD[0:-1]+t_yrAD[1:])  # ds/dt=(s2-s1)/(t2-t1), value assigned to (t2+t1)/2
    
    # First for dS_dt then for S_basin
    x = tm
    y = dSdt_basin
    f_dSdt = interp1d(x, y, kind='linear', fill_value="extrapolate")
    
    y = S_basin
    f_S = interp1d(x, y, kind='linear', fill_value="extrapolate")
    
    # New time series to interpolate to
    new_x = pr_t_yrAD

    R_ip = f_R(new_x)
    P_ip = f_P(new_x)

    dSdt_ip = f_dSdt(new_x)
    S_ip = f_S(new_x)
    
    # Convert from cm month-1 to mm month-1
    dSdt_ip = dSdt_ip*10
    
    # Estimate ET over catchment
    ET = P_ip - R_ip - dSdt_ip
    
    results = pd.DataFrame()
    results['dates'] = dates
    results = results.set_index('dates')
    results['ET'] = ET
    results['P'] = P_ip
    results['R'] = R_ip
    results['dS_dt'] = dSdt_ip
    results['S'] = S_ip*10

    results_dict[basin_name] = results
outpath = '/nfs/a68/gyjcab/datasets/et_analysis/'
np.save(outpath + 'all_basin_catchment_et_' + str(startyr) + '_' +
        str(endyr) + '_jpl_mascon_chirps_hires_Feb2020.npy', results_dict)

