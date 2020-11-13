import iris
import harmonise

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
# NB) ERA5 provides lai high and lai low - both gave comparable results
cube = iris.load_cube(path + 'lai_high_veg_on_single_level.nc')
print(cube)

harmonise.cube2netcdf(cube, 'lai_high_veg', startyr=1979, nyear=41,
                      #remove_cell_methods=True,
                      product='era5_test', regrid=True, latlon_bounds=True,
                      #time_bounds=False,
                      regrid_cube=regrid_cube)

