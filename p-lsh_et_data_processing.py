import harmonise
import numpy as np


def read_plsh_et(startyr=1982, nyear=1):
    path = '/nfs/a68/gyjcab/datasets/NTSG_ET/'
    yrs = range(1982, 2014)
    et = np.zeros((len(yrs), 12, 2160, 4320))
    for y in range(len(yrs)):
        year = yrs[y]
        fname = 'Global_Monthly_ET_' + str(year)
        print(path+fname)
        cube = harmonise.iris_read(path+fname, 'Monthly actural evapotranspirat',
                                   short_name='monthly_ET')[0]        
        data = cube.data
        data = np.rollaxis(data,2)
        et[y, :, :, :] = data[:, :, :]
        
    lat = harmonise.iris_read(path+fname, 'Latitude',
                               short_name='LAT')[0].data
    lon = harmonise.iris_read(path+fname, 'Longitude',
                               short_name='LON')[0].data
    lat =lat[:,0]
    lon = lon[0,:]
    return(et, lat, lon)


# specify path to file that matches the resolution you wish to regrid to
# 1.0 degree resolution target
path = ('/nfs/a68/gyjcab/datasets/lapse_data_harmonised/Jan_2018/mon_1.0deg/')
one_deg_cube = path+'tas_airs_mon_1.0deg_2003_2016.nc'

# 0.25 degree resolution target
path = ('/nfs/a68/gyjcab/datasets/lapse_data_harmonised/Jan_2018/mon_0.25deg/')
pt25_cube = path+'sal_clara_mon_0.25deg_1982_2015_direct_from_netcdf.nc'

# specify target cube
regrid_cube = one_deg_cube

# choose start year and number of years of data to read in
nyear = 32
startyr=1982
et, lat, lon = read_plsh_et(startyr=startyr, nyear=nyear)

# convert units from mm per month 
et = harmonise.unit_conversion(et, startyr)

args = [et, lat, lon, startyr, nyear, 'kg m^-2 s^-1']
kwargs = {'standard_name': 'water_evaporation_flux',
          'long_name': 'Evaporation',
          'short_name': 'evspsbl',
          'product': 'uni_montana_plsh_test',
          'regrid': True,
          'latlon_bounds': True,
          'time_bounds': False,
          'regrid_cube': regrid_cube}

# call harmonise.write_netcdf function to save data as new netcdf
harmonise.write_netcdf(*args, **kwargs)
