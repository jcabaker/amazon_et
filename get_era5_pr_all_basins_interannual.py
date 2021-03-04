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


def get_pixel_size(lon):
    res = 360/len(lon)
    lat = np.arange((len(lon)/2)+1)*res-90
    r=6.371*1e6
    rad=(2*pi/360)               # (m)
    da = np.nan * np.zeros((len(lat)-1))      # (m2)

    for i in range(len(lat)-1):
        da[i] = 2*pi*(1/len(lon))*r**2*(sin(rad*lat[i+1])-sin(rad*lat[i]))
    return(da)


def get_area_weighted_avg(cube, mask, pixel_size_grid):
    masked_data = np.ma.array(cube.data, mask=~mask)
    masked_weights = np.ma.array(pixel_size_grid, mask=~mask)
    avg = np.ma.average(masked_data, weights=masked_weights)
    return(avg)

# Read in reanalysis datasets
path = ('/nfs/a68/gyjcab/datasets/lapse_data_harmonised/Jan_2018/Final/0.25deg/')
startyr = 2003
endyr = 2013
constraint = iris.Constraint(time=lambda cell:
                                     datetime(startyr, 1, 1) <= cell.point <= datetime(endyr, 12, 31))

era5_pr = iris.load_cube(path+'pr*era5*deg*.nc', constraint=constraint)
era5_pr.convert_units('kg m^-2 month^-1')
era5_dates = get_dates(era5_pr)

# generate mask to extract data from basin
lats = get_lats(era5_pr)
lons = get_lons(era5_pr)

basin_shapes = ['purus_dissolved', 'madeira_dissolved',
                'negro_dissolved',  'xingu_dissolved',
                'jari_dissolved',  'japura_dissolved',
                'branco_dissolved','aripuana_dissolved',
                'solimoes_dissolved5', 'tapajos_dissolved3',
                'amazon_obidos_dissolved']

results_dict = {}
for basin in basin_shapes:
    print(basin)
    mask = extract.get_mask(lats, lons, basin)

    temp = 1*mask

    pixel_size_grid = get_pixel_size(lons)
    pixel_size_grid = np.array([pixel_size_grid]*len(lons)).transpose()

    era5_vals = []
    
    for yr in range(era5_pr.shape[0]):
        data = era5_pr[yr, :, :]
        amazon_mean = get_area_weighted_avg(data, mask, pixel_size_grid)
        era5_vals.append(amazon_mean)

    era5_df = pd.DataFrame()
    era5_df['dates'] = era5_dates
    era5_df['basin_mean'] = era5_vals
    era5_df = era5_df.set_index('dates')

    outdict = {}
    outdict['era5'] = era5_df
    
    basin_name = basin.split('_')[0]
    results_dict[basin_name] = outdict

outpath = '/nfs/a68/gyjcab/datasets/et_analysis/'
np.save(outpath + 'reanalysis_all_basins_pre_'+ str(startyr) + '_' +
        str(endyr) + '_interannual.npy', results_dict)
