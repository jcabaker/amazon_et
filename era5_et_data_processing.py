import iris
import harmonise
import numpy as np

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
cube = iris.load_cube(path + 'et_on_single_level_June2020.nc')
print(cube)

# convert cube data units
# from m to mm and from negative to positive (https://www.ecmwf.int/en/faq/how-can-evaporation-have-both-positive-and-negative-values)
cube.data = cube.data*(-1000)

## remove negative values
i = np.where(cube.data<0)
cube.data[i] = np.nan

# convert from (monthly mean of) daily to seconds
cube.data = cube.data/(60*60*24)
cube.units = 'kg m^-2 s^-1'

# call harmonise.cube2netcdf function to regrid and save as new cube
harmonise.cube2netcdf(cube, 'evspsbl', startyr=1979, nyear=41,
                      #remove_cell_methods=True,
                      product='era5_test', regrid=True, latlon_bounds=True,
                      #time_bounds=False,
                      regrid_cube=regrid_cube)

