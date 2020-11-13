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

# read in CHIRPS netcdf
path = '/nfs/a68/gyjcab/datasets/CHIRPS/'
cube = iris.load_cube(path + 'chirps-v2.0.monthly_1981_2020.nc')
print(cube)

# if needed convert units
#cube.units = 'kg m-2 month-1'
#cube.convert_units('kg m-2 day-1')

# call harmonise.cube2netcdf function to regrid and save as new cube
harmonise.cube2netcdf(cube, 'pr', startyr=1981, nyear=40,
                      remove_cell_methods=True,
                      product='test_chirps', regrid=True, latlon_bounds=True,
                      time_bounds=False,
                      regrid_cube=regrid_cube)
