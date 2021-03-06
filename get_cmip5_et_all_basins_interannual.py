import numpy as np
import iris
import iris.coord_categorisation
import pandas as pd
import matplotlib.pyplot as plt
from jpros.cube_funcs import *
from jpros import extract
from math import pi, sin
import warnings
warnings.filterwarnings("ignore")


def get_pixel_size(lat, lon):
    lat_res = 180/len(lat)
    lon_res = 360/len(lon)
    lat2 = np.arange((len(lat))+1)*lat_res-90
    #print(lat2)
    #assert False
    r=6.371*1e6
    rad=(2*pi/360)               # (m)
    da = np.nan * np.zeros((len(lat2)-1))      # (m2)

    for i in range(len(lat2)-1):
        da[i] = 2*pi*(1/len(lon))*r**2*(sin(rad*lat2[i+1])-sin(rad*lat2[i]))
    return(da)


def get_area_weighted_avg(cube, mask, pixel_size_grid):
    masked_data = np.ma.array(cube.data, mask=~mask)
    masked_weights = np.ma.array(pixel_size_grid, mask=~mask)
    avg = np.ma.average(masked_data, weights=masked_weights)
    #std = np.ma.std(masked_data, weights=masked_weights)
    return(avg)

path = '/nfs/a68/gyjcab/datasets/cmip5/evspsbl/historical/ensemble_means/'
startyr = 1994
endyr = 2004
constraint = iris.Constraint(time=lambda cell:
                             startyr <= cell.point.year <= endyr)


# models with LAI, PRE, RDN and ET data
models = ['ACCESS1-3',
          'bcc-csm1-1',
          'BNU-ESM',
          'CanESM2',
          'CCSM4',
          'CESM1-BGC',
          'FIO-ESM',
          'HadGEM2-CC',
          'HadGEM2-ES',
          'inmcm4',
          'IPSL-CM5A-LR',
          'MPI-ESM-LR',
          'NorESM1-M']


basin_shapes = ['purus_dissolved', 'madeira_dissolved',
                'negro_dissolved',  'xingu_dissolved',
                'jari_dissolved',  'japura_dissolved',
                'branco_dissolved','aripuana_dissolved',
                'solimoes_dissolved5', 'tapajos_dissolved3',
                'amazon_obidos_dissolved']

results_dict = {}

for basin in basin_shapes:
    print(basin, '----------------------------------------')
    out_dict = {}
    for model in models:
        print(model)
        cube = iris.load_cube(path+'*'+model+'_*.nc', constraint=constraint)
        
        # adjust units
        cube.units = 'kg m^-2 s^-1'
        cube.convert_units('kg m^-2 month^-1')
    
        lats = get_lats(cube)
        lons = get_lons(cube)
    
        # Reorder lons
        if lons.max() > 180:
            cube = minus180_to_plus180(cube)
            lons = get_lons(cube)
        
        if model == 'CMCC-CESM':
        # This model has historical ET as -ve values
            cube.data = cube.data*-1
        
        # generate mask to extract data from basin
        mask = extract.get_mask(lats, lons, basin)

        # find average over basin
        pixel_size_grid = get_pixel_size(lats, lons)
        print(len(pixel_size_grid))
        pixel_size_grid = np.array([pixel_size_grid]*len(lons)).transpose()
        
        monthly_means = []
        for t in range(cube.shape[0]):
            data = cube[t, :, :]
            amazon_mean = get_area_weighted_avg(data, mask, pixel_size_grid)
            monthly_means.append(amazon_mean)
            if t == 0:
                dates = get_dates(cube)
 
        out_dict[model] = monthly_means
        out_dict['dates'] = dates

    basin_name = basin.split('_')[0]
    results_dict[basin_name] = out_dict

outpath = '/nfs/a68/gyjcab/datasets/et_analysis/'
np.save(outpath + 'cmip5_all_basins_et_'+ str(startyr) + '_' +
        str(endyr) + '_interannual_trim.npy', results_dict)
