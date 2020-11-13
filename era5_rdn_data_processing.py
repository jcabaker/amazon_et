import iris
import harmonise
from cube_funcs import get_dates

# specify path to file that matches the resolution you wish to regrid to
# 1.0 degree resolution target
path = ('/nfs/a68/gyjcab/datasets/lapse_data_harmonised/Jan_2018/mon_1.0deg/')
one_deg_cube = path+'tas_airs_mon_1.0deg_2003_2016.nc'

# 0.25 degree resolution target
path = ('/nfs/a68/gyjcab/datasets/lapse_data_harmonised/Jan_2018/mon_0.25deg/')
pt25_cube = path+'sal_clara_mon_0.25deg_1982_2015_direct_from_netcdf.nc'

# specify target cube
regrid_cube = one_deg_cube

# read in ERA5 data
path = '/nfs/a68/gyjcab/datasets/ERA5/'
cube = iris.load_cube(path + 'era5_surface_solar_radiation.nc')
print(cube)

# Convert units to W/m2 by dividing by seconds in day
dates = get_dates(cube)
for t in range(len(dates)):
    date = dates[t]
    seconds_in_day = 60*60*24
    temp_data = cube.data[t, :, :] / seconds_in_day
    cube.data[t, :, :] = temp_data

# convert cube data units
cube.units = 'W/m2'

harmonise.cube2netcdf(cube, 'rdn', startyr=1979, nyear=41,
                      #remove_cell_methods=True,
                      product='era5_test', regrid=True, latlon_bounds=True,
                      #time_bounds=False,
                      regrid_cube=regrid_cube)

