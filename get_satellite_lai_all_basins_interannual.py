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

# Read in satellite datasets
path = ('/nfs/a68/gyjcab/datasets/lapse_data_harmonised/Jan_2018/Final/0.25deg/')
startyr = 2003
endyr = 2013
constraint = iris.Constraint(time=lambda cell:
                             datetime(startyr, 1, 1) <= cell.point <= datetime(endyr, 12, 31))

modis_lai = iris.load_cube(path+'lai_*modis_bu*deg*.nc', constraint=constraint)
modis_dates = get_dates(modis_lai)

# generate mask to extract data from basin
lats = get_lats(modis_lai)
lons = get_lons(modis_lai)

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
    plt.figure()

    pixel_size_grid = get_pixel_size(lons)
    pixel_size_grid = np.array([pixel_size_grid]*len(lons)).transpose()

    modis_vals = []
    
    for yr in range(modis_lai.shape[0]):
        data = modis_lai[yr, :, :]
        amazon_mean = get_area_weighted_avg(data, mask, pixel_size_grid)
        modis_vals.append(amazon_mean)

    modis_df = pd.DataFrame()
    modis_df['dates'] = modis_dates
    modis_df['basin_mean_lai'] = modis_vals
    modis_df = modis_df.set_index('dates')

    outdict = {}
    outdict['modis'] = modis_df
    
    basin_name = basin.split('_')[0]
    results_dict[basin_name] = outdict

outpath = '/nfs/a68/gyjcab/datasets/et_analysis/'

np.save(outpath + 'satellite_all_basins_modis_bu_lai_'+ str(startyr) + '_' +
        str(endyr) + '_interannual.npy', results_dict)

