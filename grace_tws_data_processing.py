import iris
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

# GRACE Monthly Mass Grids - Global mascons (JPL RL06_v02)
# read scale
path = '/nfs/a68/gyjcab/datasets/GRACE/JPL_MASCON/'
scale = iris.load_cube(path+'CLM4.SCALE_FACTOR.JPL.MSCNv02CRI.nc')

# read liquid water equivalent thickness
name_constraint = iris.Constraint(cube_func=lambda cube:
                                  cube.var_name == 'lwe_thickness')
lwe = iris.load_cube(path+'GRCTellus.JPL.200204_201911.GLO.RL06M.MSCNv02CRI.nc',
                      constraint=name_constraint)

name = lwe.name()
cube = lwe*scale.data

# call harmonise.cube2netcdf function to regrid and save as new cube
harmonise.cube2netcdf(cube, 'lwe', startyr=2002, nyear=19,
                      product='test_grace_jpl_mascon', regrid=True, latlon_bounds=True,
                      regrid_cube=regrid_cube, time_bounds=False, name=name)
