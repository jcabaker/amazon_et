#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import iris
import harmonise
from iris.experimental.equalise_cubes import equalise_attributes
from iris.util import unify_time_units

# specify path to file that matches the resolution you wish to regrid to
# 1.0 degree resolution target
path = ('/nfs/a68/gyjcab/datasets/lapse_data_harmonised/Jan_2018/mon_1.0deg/')
one_deg_cube = path+'tas_airs_mon_1.0deg_2003_2016.nc'

# 0.25 degree resolution target
path = ('/nfs/a68/gyjcab/datasets/lapse_data_harmonised/Jan_2018/mon_0.25deg/')
pt25_cube = path+'sal_clara_mon_0.25deg_1982_2015_direct_from_netcdf.nc'

# specify target cube
regrid_cube = one_deg_cube

# read in merged MODIS et data (merged in separate script)
data_path = '/nfs/a68/gyjcab/datasets/MODIS_ET/hdf_files_V006/data/final_files/'
cubes = iris.load(data_path +  'MOD16A2*_average_interpolation.nc')
equalise_attributes(cubes)
unify_time_units(cubes)
print(cubes[0])

# remove coordinate system
for cube in cubes:
    cube.remove_coord('month')
    cube.convert_units('kg m-2 s-1')
    #print(cube)
    cube.coord('time').coord_system = None
    cube.coord('latitude').coord_system = None
    cube.coord('longitude').coord_system = None

# call harmonise.cube2netcdf function to regrid and save as new cube
harmonise.cube2netcdf(cubes, 'evspsbl', startyr=2001, nyear=19,merge=True,
                      product='modis_mod16a2_test', regrid=True, latlon_bounds=True,
                      regrid_cube=regrid_cube, time_bounds=False)

