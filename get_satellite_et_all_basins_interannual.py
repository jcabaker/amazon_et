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
# MODIS
modis_et = iris.load_cube(path+'evspsbl*modis_mod16a2*deg*2019.nc', constraint=constraint)
modis_et.convert_units('kg m^-2 month^-1')
modis_dates = get_dates(modis_et)

# P-LSH
ntsg_et = iris.load_cube(path+'evspsbl_uni_montana_gls_*deg_1982_2013.nc',
                                     constraint=constraint)
ntsg_et.convert_units('kg m^-2 month^-1')
ntsg_dates = get_dates(ntsg_et)

# GLEAM
gleam_et = iris.load_cube(path+'evspsbl_gleam_3.3b_*deg_2003_2018.nc',
                                     constraint=constraint)
gleam_et.convert_units('kg m^-2 month^-1')
gleam_dates = get_dates(gleam_et) 

# generate mask to extract data from basin
lats = get_lats(modis_et)
lons = get_lons(modis_et)


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
    ntsg_vals = []
    gleam_vals = []
    
    for yr in range(modis_et.shape[0]):
        data = modis_et[yr, :, :]
        amazon_mean = get_area_weighted_avg(data, mask, pixel_size_grid)
        modis_vals.append(amazon_mean)
    
    for yr in range(gleam_et.shape[0]):
        data = gleam_et[yr, :, :]
        amazon_mean = get_area_weighted_avg(data, mask, pixel_size_grid)
        gleam_vals.append(amazon_mean)

    for yr in range(ntsg_et.shape[0]):
        data = ntsg_et[yr, :, :]
        amazon_mean = get_area_weighted_avg(data, mask, pixel_size_grid)
        ntsg_vals.append(amazon_mean)
    
    modis_df = pd.DataFrame()
    modis_df['dates'] = modis_dates
    modis_df['basin_mean_et'] = modis_vals
    modis_df = modis_df.set_index('dates')

    ntsg_df = pd.DataFrame()
    ntsg_df['dates'] = ntsg_dates
    ntsg_df['basin_mean_et'] = ntsg_vals
    ntsg_df = ntsg_df.set_index('dates')
   
    gleam_df = pd.DataFrame()
    gleam_df['dates'] = gleam_dates[0:-3]
    gleam_df['basin_mean_et'] = gleam_vals[0:-3]
    gleam_df = gleam_df.set_index('dates')

    outdict = {}
    outdict['modis'] = modis_df
    outdict['ntsg'] = ntsg_df
    outdict['gleam'] = gleam_df
    
    basin_name = basin.split('_')[0]
    results_dict[basin_name] = outdict

outpath = '/nfs/a68/gyjcab/datasets/et_analysis/'
np.save(outpath + 'satellite_all_basins_et_'+ str(startyr) + '_' + 
        str(endyr) + '_interannual.npy', results_dict)

