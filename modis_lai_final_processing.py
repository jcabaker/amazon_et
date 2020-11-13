#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import iris
import iris.coord_categorisation
from iris.experimental.equalise_cubes import equalise_attributes
from iris.util import unify_time_units
import numpy as np
import datetime
import cf_units
import warnings
from netCDF4 import date2num
from cube_funcs import get_lats
warnings.filterwarnings("ignore")
#%%
# Define path to files
main_path = '/nfs/a68/ee13c2s/python/datasets/lai_modis'

# Define date info
units = 'days since ' + str(2000) + '-01-01 00:00:0.0'
time_unit = cf_units.Unit(units, calendar='gregorian')

# For each 8-day file, read data, add date, convert units, and add to list of cubes
for yr in range(2001, 2019):
    cubes = []
    cube = []
    year = str(yr)
    print(year, '---------------------------------------------------------')
    for doy in range(1, 365, 8):
        print(doy)
        doy_str = str(doy).zfill(3)
        fpath = main_path + '/' + year + '/' + doy_str + '/'
        print(fpath)
        fname = 'merged_0.05_average_interp.nc'
        try:
            cube = iris.load_cube(fpath + fname)
            print(cube)

            # add date to cube
            date = datetime.datetime(yr,1,1) + datetime.timedelta(doy-1)
            times = date2num(date, units=units, calendar='gregorian')
            time_unit = cf_units.Unit(units, calendar='gregorian')
            time = iris.coords.DimCoord(times, standard_name='time',
                                                        units=time_unit)
            cube = iris.util.new_axis(cube)
            cube.add_dim_coord(time, 0)

            # add cube name
            cube.name = 'leaf_area_index'
            cube.standard_name = 'leaf_area_index'

            # divide by nday to get units in per day
            cube.data = cube.data * 0.1 
          
            # add units and convert
            cube.units = 'm2 m-2'
            print(date)
            print(cube.data.min(), cube.data.max())

        except OSError:
            pass
        
    # Fix to merge into single cube
    print(len(cubes))
    cubes = iris.cube.CubeList(cubes)
    equalise_attributes(cubes)
    unify_time_units(cubes)

    cubes2 = []
    for cube in cubes:
        lats = get_lats(cube)
        print(lats)
        temp = cubes[0].copy()
        if lats.max() > 70:
            i = np.where(lats <= 70)
            print(len(i))
            temp.data = cube.data[0:2600, :]
        else:
            temp.data = cube.data
        temp.coord('time').points = cube.coord('time').points
        cubes2.append(temp)

    cubes2 = iris.cube.CubeList(cubes2)

    try:
        cube = cubes2.merge_cube()
    except:
        cube = cubes2.concatenate_cube()
    print(cube)

    # convert to monthly
    iris.coord_categorisation.add_month(cube, 'time', 'month')
    month_cube1 = cube.aggregated_by('month', iris.analysis.MEAN)
    iris.save(month_cube1, main_path + 'final_files/MOD15A2.A' + year +
            '_average_interpolation.nc')

