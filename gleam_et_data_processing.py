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

# read in GLEAM netcdf
data_path = '/nfs/a68/gyjcab/datasets/GLEAM/v3.3/v3.3b/monthly/'
#cube = iris.load_cube(data_path + 'E_1980_2018_GLEAM_v3.3a_MO.nc')
cube = iris.load_cube(data_path + 'E_2003_2018_GLEAM_v3.3b_MO.nc')

# reorder coordinates
cube.transpose([0, 2, 1])
print(cube)
cube.standard_name = 'water_evaporation_flux'
name = 'water_evaporation_flux'
cube.convert_units('mm.s-1')
cube.units = 'kg m^-2 s^-1'

# call harmonise.cube2netcdf function to regrid and save as new cube
harmonise.cube2netcdf(cube, 'evspsbl', startyr=2003, nyear=16,
                      product='gleam_3.3b_test', regrid=True, latlon_bounds=True,
                      regrid_cube=regrid_cube, time_bounds=False, name=name)

   
