import iris
import numpy as np
import matplotlib.pyplot as plt
from iris.experimental.regrid import regrid_weighted_curvilinear_to_rectilinear
from iris.coord_systems import GeogCS
from datetime import datetime


def latent_heat_flux_to_mmpday(cube):

    """Function to convert latent heat flux to total ET"""

    if (cube.units == iris.unit.Unit('W m-2')):
        outcube = cube * (86400./2.501e6)
        outcube.units = iris.unit.Unit('mm day-1')
        outcube.standard_name = cube.standard_name

    if (cube.units != iris.unit.Unit('W m-2')):
        raise ValueError('cube not in W m-2 ', cube.units)

    return(outcube)


def monthly_anom_cube(cube, fill=None):
    ds = np.array(cube.data)
    if fill is not None:
        ds[np.where(ds == fill)] = np.nan

    if len(ds.shape) == 3:
        ds = ds.reshape(-1, 12, cube.shape[-2], cube.shape[-1])
    ds = np.array(ds)
    anomalies = np.zeros((ds.shape))
    anomalies[:] = np.nan
    for mn in range(12):
        anomalies[:, mn, :, :] = ds[:, mn, :, :] - \
                                 np.nanmean(ds[:, mn, :, :], axis=0)
#        print(np.nanmin(anomalies), np.nanmax(anomalies))
    cube2 = cube.copy()
    cube2.data = anomalies.reshape((-1, cube.shape[-2], cube.shape[-1]))
    return(cube2)


def minus180_to_plus180(var_cube):
    """
    Function to reorder cube data from -180 to +180.
    """
    # Reorganise data
    var = var_cube.data
    lat = var_cube.coord('latitude').points
    if len(lat.shape) > 1:
        plt.figure()
        plt.imshow(lat)
        lat = lat[:,0]
    lon = var_cube.coord('longitude').points
    if len(lon.shape) > 1:
        plt.figure()
        plt.imshow(lon)
        lon = lon[0,:]
    l = int(var.shape[-1]/2)
    
    if len(var_cube.shape) > 2:
        if len(var_cube.shape) == 3:
            temp1 = var[:, :, 0:l]
            temp2 = var[:, :, l:]
            new_var = np.concatenate((temp2, temp1), axis=2)
        if len(var_cube.shape) == 4:
            temp1 = var[:, :, :, 0:l]
            temp2 = var[:, :, :, l:]
            new_var = np.concatenate((temp2, temp1), axis=3)
    if len(var_cube.shape) == 2:
        temp1 = var[:, 0:l]
        temp2 = var[:, l:] 
        new_var = np.concatenate((temp2, temp1), axis=1)
    
    a = lon[int(len(lon)/2):]
    b = lon[:int(len(lon)/2)]
    
    new_lon = np.concatenate((a-360, b))
    
    # Save re-ordered data as new cube
#    try:
#        new_cube = var_cube.copy()
#        new_cube.data = new_var
#        new_cube.coord('longitude').points = new_lon
#    except ValueError:
    
    ### Make fresh cube
    if len(var_cube.shape) == 3:
        ### Establish lat and lon dimensions
        latitude = iris.coords.DimCoord(lat, standard_name='latitude',
                                        units='degrees')
        longitude = iris.coords.DimCoord(new_lon, standard_name='longitude',
                                         units='degrees')
        times = var_cube.coord('time').points
        time_unit = var_cube.coord('time').units
        time = iris.coords.DimCoord(times, standard_name='time', units=time_unit)
        
        # Call cube
        new_cube = iris.cube.Cube(new_var, 
                                  dim_coords_and_dims=
                                  [(time, 0), (latitude, 1), (longitude, 2)])
        new_cube.units = var_cube.units
        new_cube.coord('time').guess_bounds()
        new_cube.coord('longitude').guess_bounds()
        new_cube.coord('latitude').guess_bounds()

    elif len(var_cube.shape) == 4:
        ### Establish lat and lon dimensions
        latitude = iris.coords.DimCoord(lat, standard_name='latitude',
                                        units='degrees')
        longitude = iris.coords.DimCoord(new_lon, standard_name='longitude',
                                         units='degrees')
        depths = var_cube.coord('depth').points
        depth = iris.coords.DimCoord(depths, standard_name='depth', units='m')
        times = var_cube.coord('time').points
        time_unit = var_cube.coord('time').units
        time = iris.coords.DimCoord(times, standard_name='time', units=time_unit)

        # Call cube
        new_cube = iris.cube.Cube(new_var,
                                  dim_coords_and_dims=
                                  [(time, 0), (depth, 1), (latitude, 2), (longitude, 3)])
        new_cube.units = var_cube.units
        new_cube.coord('time').guess_bounds()
        new_cube.coord('longitude').guess_bounds()
        new_cube.coord('latitude').guess_bounds()
        new_cube.coord('depth').guess_bounds()
        
    if len(var_cube.shape) == 2:
        ### Establish lat and lon dimensions
        latitude = iris.coords.DimCoord(lat, standard_name='latitude',
                                        units='degrees')
        longitude = iris.coords.DimCoord(new_lon, standard_name='longitude',
                                         units='degrees')
        
        # Call cube
        new_cube = iris.cube.Cube(new_var, 
                                  dim_coords_and_dims=
                                  [(latitude, 0), (longitude, 1)])
        new_cube.units = var_cube.units
        new_cube.coord('longitude').guess_bounds()
        new_cube.coord('latitude').guess_bounds()

    print(new_cube.data.max())
    
    if new_cube.data.max() > 1e20:
        new_cube.data[new_cube.data==new_cube.data.max()] = np.nan
        print(new_cube.data.max())
    return(new_cube)


def get_dates(cube, verbose=False):
    dates = cube.coord('time').units.num2date(cube.coord('time').points)
    dates = [datetime(date.year, date.month, date.day) for date in dates]
    if verbose is True:
        print(dates)
    else:
        print(dates[0], '–', dates[-1])
    return(dates)


def get_lats(cube):
    try:
        lats = cube.coords('latitude').points
    except AttributeError:
        lats = cube.coords('latitude')[0][:].points
    return(lats)
    
    
def get_lons(cube):
    try:
        lons = cube.coords('longitude').points
    except AttributeError:
        lons = cube.coords('longitude')[0][:].points
    return(lons)
    

def dummy_cube(lat_values, lon_values):
    """Make a dummy cube with desired grid."""
        
    latitude = iris.coords.DimCoord(lat_values,
                                    standard_name='latitude',
                                    units='degrees_north',
                                    coord_system=None)
    longitude = iris.coords.DimCoord(lon_values,                     
                                     standard_name='longitude',
                                     units='degrees_east',
                                     coord_system=None)

    dummy_data = np.zeros((len(lat_values), len(lon_values)))
    new_cube = iris.cube.Cube(dummy_data, dim_coords_and_dims=[(latitude, 0), (longitude, 1)])
    
    return(new_cube)
    
 
def regrid_curvilinear_cmip(src_cube):
    #print(src_cube.shape)
    
    weights = np.ones((src_cube.shape[-2], src_cube.shape[-1]))
    lat_pix_size = np.diff(src_cube.coord('latitude')[:,0].points).mean()
    
    latmin = src_cube.coord('latitude')[:,0].points.min()
    lats = [(x*abs(lat_pix_size))+latmin for x in range(src_cube.shape[-2])]
    lons = src_cube.coord('longitude').points[0,:]
    target_grid_cube = dummy_cube(lats, lons)
    target_grid_cube.coord('longitude').guess_bounds()
    target_grid_cube.coord('latitude').guess_bounds()
    # Add cube coord system
#    target_grid_cube.coord('latitude').coord_system = GeogCS(iris.fileformats.pp.EARTH_RADIUS)
#    target_grid_cube.coord('longitude').coord_system = GeogCS(iris.fileformats.pp.EARTH_RADIUS)
    
    
    regridded_cube = iris.cube.Cube(np.nan*np.zeros((src_cube.shape)))
    time = src_cube.coord('time')
    latitude = iris.coords.DimCoord(lats,
                                    standard_name='latitude',
                                    units='degrees_north',
                                    coord_system=None)
    longitude = iris.coords.DimCoord(lons,                     
                                     standard_name='longitude',
                                     units='degrees_east',
                                     coord_system=None)
    regridded_cube.add_dim_coord(time, 0)
    regridded_cube.add_dim_coord(latitude, 1)
    regridded_cube.add_dim_coord(longitude, 2)
    print(regridded_cube)
    #assert False
    
    try:
        if len(src_cube.shape) > 2:
            time = src_cube.shape[0]
            for t in range(time):
                temp = regrid_weighted_curvilinear_to_rectilinear(src_cube[t, :, :], 
                                                                  weights, 
                                                                  target_grid_cube)
                regridded_cube.data[t, :, :] = temp.data
        else:
            regridded_cube.data = regrid_weighted_curvilinear_to_rectilinear(src_cube, 
                                                                        weights, 
                                                                        target_grid_cube)
    except ValueError:
        src_cube.coord('latitude').coord_system = GeogCS(6371229)
        src_cube.coord('longitude').coord_system = GeogCS(6371229)
        target_grid_cube.coord('latitude').coord_system = GeogCS(6371229)
        target_grid_cube.coord('longitude').coord_system = GeogCS(6371229)
        if len(src_cube.shape) > 2:
            time = src_cube.shape[0]
            for t in range(time):
                temp = regrid_weighted_curvilinear_to_rectilinear(src_cube[t, :, :], 
                                                                  weights, 
                                                                  target_grid_cube)
                regridded_cube.data[t, :, :] = temp.data
        else:
            regridded_cube.data = regrid_weighted_curvilinear_to_rectilinear(src_cube, 
                                                                        weights, 
                                                                        target_grid_cube)
    return(regridded_cube)


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


def get_max(fname):
    cube = iris.load_cube(fname)
    print('MAX', np.nanmax(cube.data))


def get_min(fname):
    cube = iris.load_cube(fname)
    print('MIN', np.nanmin(cube.data))
