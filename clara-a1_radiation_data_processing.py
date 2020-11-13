import harmonise
import warnings
warnings.filterwarnings("ignore")

# specify path to file that matches the resolution you wish to regrid to
# 1.0 degree resolution target
path = ('/nfs/a68/gyjcab/datasets/lapse_data_harmonised/Jan_2018/mon_1.0deg/')
one_deg_cube = path+'tas_airs_mon_1.0deg_2003_2016.nc'

# 0.25 degree resolution target
path = ('/nfs/a68/gyjcab/datasets/lapse_data_harmonised/Jan_2018/mon_0.25deg/')
pt25_cube = path+'sal_clara_mon_0.25deg_1982_2015_direct_from_netcdf.nc'

# specify target cube
regrid_cube = one_deg_cube

# read in CLARA radiation data
data_path = '/nfs/a68/gyjcab/datasets/CLARA/surface_radiation/sis/'
cubes = harmonise.iris_read(data_path, 'surface_downwelling_shortwave_flux',
                            short_name='SIS')
nyear = len(cubes)/12

# call harmonise.cube2netcdf function to regrid and save as new cube
harmonise.cube2netcdf(cubes, 'sis', startyr=1982, nyear=nyear,
                      product='clara_test', regrid=True, latlon_bounds=True,
                      merge=True, regrid_cube=regrid_cube, units='W m^-2')
