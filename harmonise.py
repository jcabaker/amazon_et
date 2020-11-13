  #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 12 09:32:41 2017

@author: earjba
"""
import cf_units
import numpy as np
import iris
import iris.coord_categorisation
from iris.experimental.equalise_cubes import equalise_attributes
from iris.util import unify_time_units
from datetime import datetime, timedelta
from netCDF4 import date2num, num2date
import warnings
warnings.filterwarnings("ignore")

def get_lat_bounds(array1d):
    div = abs(array1d[1] - array1d[0])
    if array1d[0] < 0:
        extra_val = array1d[0] - div
        bounds1d = np.concatenate(([extra_val], array1d))
    else:
        extra_val = array1d[-1] - div
        bounds1d = np.concatenate((array1d, [extra_val]))
    bounds2d = np.hstack((bounds1d[:-1, np.newaxis], bounds1d[1:, np.newaxis]))
    bounds2d = bounds2d.astype('float')
    return(bounds2d)


def get_lon_bounds(array1d):
    div = abs(array1d[1] - array1d[0])
    extra_val = array1d[-1] + div
    bounds1d = np.concatenate((array1d, [extra_val]))
    bounds2d = np.hstack((bounds1d[:-1, np.newaxis], bounds1d[1:, np.newaxis]))
    bounds2d = bounds2d.astype('float')
    return(bounds2d)
    

def get_time_bounds(time):
    extra_val = time[-1] + 31
    bounds1d = np.concatenate((time, [extra_val]))
    bounds2d = np.hstack((bounds1d[:-1, np.newaxis], bounds1d[1:, np.newaxis]))
    return(bounds2d)


def write_netcdf(var, lat, lon, startyr, nyear, varunits,
                 standard_name=None, long_name=None, short_name=None,
                 product=None, regrid=False,
                 latlon_bounds=True, time_bounds=True, guess=False,
                 path='/nfs/a68/gyjcab/datasets/lapse_data_harmonised/Jan_2018/Final/',
                 regrid_cube=None, convert_monthly=False,
                 cf=True,
                 scheme=iris.analysis.AreaWeighted(mdtol=0.5)):
    if len(var.shape) > 3:
        var = var.reshape((-1, var.shape[-2], var.shape[-1]))
    print(var.shape)
    # Check data orientation
    if lat[0] > lat[-1]:
        # Flip lat and associated index
        lat = lat[::-1]
        if len(var.shape) == 2:
            var = var[::-1, :]
        elif len(var.shape) == 3:
            var = var[:, ::-1, :]

    # Create iris data cube

    # First establish time coordinates
    if nyear != 0:
        calendar = 'gregorian'
        units = 'days since ' + str(startyr) + '-01-01 00:00:0.0'
        dates = []
        if var.shape[0] == nyear:
            for yr in range(nyear):
                year = yr+startyr
                dates.append(datetime(year, 1, 1))
            print(dates)
        elif var.shape[0]/nyear < 365:
            for yr in range(nyear):
                year = yr+startyr
                if int(var.shape[0]/nyear) == 12:
                    for mn in range(1, 12+1):
                        dates.append(datetime(year, mn, 1))
                elif var.shape[0]/nyear == 46:
                    for n in range(46):
                        dates.append(datetime(year=year, month=1, day=1) + n *
                                     timedelta(days=8))
        elif var.shape[0]/nyear >= 365:
            for n in range(var.shape[0]):
                dates.append(datetime(year=startyr, month=1, day=1) + n *
                timedelta(days=1)) 
        print(dates[0:10])
        print(dates[-10:])
        times = date2num(dates, units=units, calendar=calendar)
        time_unit = cf_units.Unit(units, calendar=calendar)
        time = iris.coords.DimCoord(times, standard_name='time', 
                                    units=time_unit)

    # Next establish lat and lon dimensions
    latitude = iris.coords.DimCoord(lat, standard_name='latitude',
                                    units='degrees')
    longitude = iris.coords.DimCoord(lon, standard_name='longitude',
                                     units='degrees')

    # Other attributes
    today = datetime.today()
    history = "Created " + today.strftime("%H:%M:%S %d/%m/%Y")
    data_type = str(var.dtype)
    if cf is True:
        attributes = {'history': history, 'data_type': data_type,
                      'Conventions': 'CF-1.5', 'regridded': str(regrid)}
        
    else:
        attributes = {'history': history, 'data_type': data_type,
                      'regridded': str(regrid)}
    # Call cube
    if nyear == 0:
        cube = iris.cube.Cube(var, var_name=short_name,
                          standard_name=standard_name,
                          long_name=long_name,
                          units=varunits,
                          dim_coords_and_dims=[(latitude, 0), (longitude, 1)],
                          attributes=attributes)
    else:
        cube = iris.cube.Cube(var, var_name=short_name,
                          standard_name=standard_name,
                          long_name=long_name,
                          units=varunits,
                          dim_coords_and_dims=[(time, 0), (latitude, 1),
                                               (longitude, 2)],
                          attributes=attributes)
    print('')
    print(cube)
    
    # if data not monthly convert to monthly 
    # Call cube
    if convert_monthly is True:
        iris.coord_categorisation.add_month(cube, 'time', name='month')
        iris.coord_categorisation.add_year(cube, 'time', name='year') 
        month_cube = cube.aggregated_by(['month', 'year'], iris.analysis.MEAN)
        time = month_cube.coord('time')
        latitude = month_cube.coord('latitude')
        longitude = month_cube.coord('longitude')
        cube = iris.cube.Cube(month_cube.data, var_name=short_name,
                              standard_name=standard_name,
                              long_name=long_name,
                              units=varunits,
                              dim_coords_and_dims=[(time, 0), (latitude, 1),
                                                   (longitude, 2)],
                              attributes=attributes)
        print('')
        print(cube)
    
    # Add bounds information
    if time_bounds is True and guess is False:
        cube.coord('time').bounds = get_time_bounds(cube.coord('time').points)
    elif time_bounds is True and guess is True:
        cube.coord('time').guess_bounds()
        
    if latlon_bounds is True and guess is False:   
        lons = cube.coord('longitude').points
        lats = cube.coord('latitude').points
        cube.coord('longitude').bounds = get_lon_bounds(lons)
        cube.coord('latitude').bounds = get_lat_bounds(lats)
    elif latlon_bounds is True and guess is True:  
        cube.coord('longitude').guess_bounds()
        cube.coord('latitude').guess_bounds()
    
    # Regrid if required - currently using linear interpolation
    if regrid is True:
        target_cube = iris.load_cube(regrid_cube)
        #target_cube.coord('time').bounds = get_time_bounds(target_cube.coord('time').points)
        target_cube.coord('longitude').bounds = get_lon_bounds(target_cube.coord('longitude').points)
        target_cube.coord('latitude').bounds = get_lat_bounds(target_cube.coord('latitude').points)
        cube = cube.regrid(target_cube, scheme)
        print('')
        print('Regridded cube:')
        print(cube)
    
    # Save as new netcdf file
    res = str(360/(len(cube.coord('longitude').points)))
    if nyear == 0:
        new_fname = short_name + '_' + product + '_' + 'mon_' + res + 'deg.nc'
    else:
        new_fname = short_name + '_' + product + '_' + 'mon_' + res +'deg_' +\
                str(startyr) + '_' + str(startyr+nyear-1) + '.nc'

    iris.save(cube, path+new_fname)
    


def iris_read(data_path, standard_name, short_name=None):
    cubes = iris.load(data_path + '*.nc', standard_name)
    if short_name is not None:
        var_name_temp = iris.Constraint(cube_func=lambda cube:
                                        cube.var_name == short_name)
        cubes = cubes.extract(var_name_temp)
    return(cubes)

   
def cube2netcdf(cubes, var_name, startyr=2000, nyear=10, product=None,
                regrid=True, latlon_bounds=True, time_bounds=True,
                guess=False, equalise=True, merge=False,
                path='/nfs/a68/gyjcab/datasets/lapse_data_harmonised/Jan_2018/Final/',
                regrid_cube=None, name=None, units=None,
                convert_monthly=False, remove_cell_methods=False, 
                convert_unit_scale=None, cf=True,
                scheme=iris.analysis.AreaWeighted(mdtol=0.5)):
    
    if merge is True:
        if equalise is True:
            equalise_attributes(cubes)
            unify_time_units(cubes)
            try:
                cube = cubes.merge_cube()
            except:
                cube = cubes.concatenate_cube()
        else:
            cube = cubes
    else:
        cube = cubes
    if name is None:
        name = cube.name()
        print(name)
    
    # Add bounds information
    if time_bounds is True and guess is False:
        cube.coord('time').bounds = get_time_bounds(cube.coord('time').points)
    elif time_bounds is True and guess is True:
        cube.coord('time').guess_bounds()
        
    if latlon_bounds is True and guess is False:   
        lons = cube.coord('longitude').points
        lats = cube.coord('latitude').points
        cube.coord('longitude').bounds = get_lon_bounds(lons)
        cube.coord('latitude').bounds = get_lat_bounds(lats)
    elif latlon_bounds is True and guess is True:  
        cube.coord('longitude').guess_bounds()
        cube.coord('latitude').guess_bounds()
    
    # if data not monthly convert to monthly 
    # Call cube
    if convert_monthly is True:
        iris.coord_categorisation.add_month(cube, 'time', name='month')
        iris.coord_categorisation.add_year(cube, 'time', name='year') 
        month_cube = cube.aggregated_by(['month', 'year'], iris.analysis.MEAN)
        standard_name = month_cube.standard_name
        long_name = month_cube.long_name
        if units != None:
            varunits = units
        else:
            varunits = month_cube.units
        time = month_cube.coord('time')
        latitude = month_cube.coord('latitude')
        longitude = month_cube.coord('longitude')
        today = datetime.today()
        history = "Created " + today.strftime("%H:%M:%S %d/%m/%Y")
        if cf is True:
            attributes = {'history': history, 
                          'Conventions': 'CF-1.5',
                          'regridded': str(regrid)}
        else:
            attributes = {'history': history, 
                          'regridded': str(regrid)}
        cube = iris.cube.Cube(month_cube.data, var_name=var_name,
                              standard_name=standard_name,
                              long_name=long_name,
                              units=varunits,
                              dim_coords_and_dims=[(time, 0), (latitude, 1),
                                                   (longitude, 2)],
                              attributes=attributes)
        print('')
        print(cube)
        
    if convert_unit_scale != None:        
        cube.data = cube.data*convert_unit_scale
    if units != None:
        cube.units = units
        
    if remove_cell_methods is True:
        month_cube = cube
        standard_name = month_cube.standard_name
        long_name = month_cube.long_name
        if units != None:
            varunits = units
        else:
            varunits = month_cube.units
        time = month_cube.coord('time')
        latitude = month_cube.coord('latitude')
        longitude = month_cube.coord('longitude')
        today = datetime.today()
        history = "Created " + today.strftime("%H:%M:%S %d/%m/%Y")
        data_type = str(month_cube.data.dtype)
        if cf is True:
            attributes = {'history': history,
                          'Conventions': 'CF-1.5',
                          'regridded': str(regrid),
                          'data_type': data_type}
        else:
            attributes = {'history': history,
                          'regridded': str(regrid),
                          'data_type': data_type}
        if (month_cube.data.shape[1]>month_cube.data.shape[2]):
            data = np.swapaxes(month_cube.data,2,1)
        else:
            data = month_cube.data
        cube = iris.cube.Cube(data, var_name=var_name,
                              standard_name=standard_name,
                              long_name=long_name,
                              units=varunits,
                              dim_coords_and_dims=[(time, 0), (latitude, 1),
                                                   (longitude, 2)],
                              attributes=attributes)
    ### regrid if required
    if regrid is True:            
        target_cube = iris.load_cube(regrid_cube)
        if time_bounds is True:
            target_cube.coord('time').bounds = get_time_bounds(target_cube.coord('time').points)
        target_cube.coord('longitude').bounds = get_lon_bounds(target_cube.coord('longitude').points)
        target_cube.coord('latitude').bounds = get_lat_bounds(target_cube.coord('latitude').points)
        new_cube = cube.regrid(target_cube, scheme)

    elif (nyear == 0) and (regrid is True):
        target_cube = iris.load_cube(regrid_cube)
        new_cube = cube.regrid(target_cube, scheme)
            
    else:
        new_cube = cube
    
    
    new_cube.rename(name)
    if units != None:
        new_cube.units = units
    print(new_cube)
    res = str(360/(len(new_cube.coord('longitude').points)))
    if nyear == 0:
        new_fname = path + var_name + '_' + product + '_' +\
                    'mon_'+ res + 'deg.nc'
    else:
        new_fname = path + var_name + '_' + product + '_' + 'mon_'+ res +\
                'deg_' + str(startyr) + '_' + str(int(startyr+nyear-1)) +\
                '.nc'
    print(new_fname)
    print(new_cube)
    iris.save(new_cube, new_fname)
    

def unit_conversion(var, startyr):
    new_var = np.zeros((var.shape))
    if var.shape[0] < 365:
        for yr in range(var.shape[0]):
            year = startyr + yr
            if year % 4 == 0:
                no_days = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            else:
                no_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            for mn in range(12):
                new_var[yr, mn, :, :] = var[yr, mn, :, :]/(60*60*24*no_days[mn])
    else:
        new_var = var/(60*60*24)
    return(new_var)
