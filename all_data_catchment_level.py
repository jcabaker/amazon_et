"""
Script to create table of catchment-mean ET, P, RDN and LAI estimates
@author: Jess Baker, j.c.baker@leeds.ac.uk
"""

import pandas as pd
import numpy as np
from datetime import datetime


fpath = '/nfs/a68/gyjcab/datasets/et_analysis/'

fnames = [# catchment data
          'all_basin_catchment_et_2002_2019_jpl_mascon_chirps_hires.npy',

          # satellite data
          'satellite_all_basins_et_2003_2013_interannual.npy',
          'satellite_all_basins_rdn_2003_2013_interannual.npy',
          'satellite_all_basins_modis_mod15a2h_lai_2003_2013_interannual.npy',

          # reanalysis data
          'reanalysis_all_basins_et_2003_2013_interannual.npy',
          'reanalysis_all_basins_pre_2003_2013_interannual.npy',
          'reanalysis_all_basins_rdn_2003_2013_interannual.npy',
          'reanalysis_all_basins_lai_high_2003_2013_interannual.npy',

          # cmip5 data
          'cmip5_all_basins_et_1994_2004_interannual_trim.npy',
          'cmip5_all_basins_pr_1994_2004_interannual_trim.npy',
          'cmip5_all_basins_rdn_1994_2004_interannual_trim.npy',
          'cmip5_all_basins_lai_1994_2004_interannual_trim.npy',

          # cmip6 data
          'cmip6_all_basins_et_2003_2013_interannual.npy',
          'cmip6_all_basins_pr_2003_2013_interannual.npy',
          'cmip6_all_basins_rdn_2003_2013_interannual.npy',
          'cmip6_all_basins_lai_2003_2013_interannual.npy']

columns = ['date', 'catchment', 'product', 'variable', 'data']
all_df = pd.DataFrame(columns=columns)

#fnames = ['satellite_all_basins_et_2003_2013_interannual.npy']
#fnames = [#'cmip6_all_basins_et_2003_2013_interannual.npy',
#          'cmip6_all_basins_pr_2003_2013_interannual.npy']
#          #'cmip6_all_basins_rdn_2003_2013_interannual.npy',
#          #'cmip6_all_basins_lai_2003_2013_interannual.npy']

counter = 0
for fname in fnames:
    print(fname)

    if 'all_basin_catchment_et' in fname:
        pass
    else:
        variable = fname.split('_')[3].upper()

    data = np.load(fpath+fname, allow_pickle=True).item()
    catchments = data.keys()

    #for catchment in catchments:
    for catchment in ['amazon']:    
        
        catchment_data = data[catchment]
        #print(catchment_data)
        #print(catchment_data.keys())
        for variable_key in catchment_data.keys():
            #print(variable_key)
            temp_df = pd.DataFrame(columns=columns)
            df = catchment_data[variable_key]
            #print(df)
             
            if 'all_basin_catchment_et' in fname:
                if variable_key in ['ET', 'R', 'P', 'dS_dt']:
                    datemin = datetime(2003, 1, 1, 0, 0)
                    datemax = datetime(2013, 12, 1, 0, 0)
                    idx = pd.date_range(datemin, datemax, freq='MS')
                    df = df.reindex(idx, fill_value=np.nan)
                    temp_df['date'] = df.index
                    temp_df['catchment'] = catchment
                    temp_df['variable'] = variable_key
                    if variable_key == 'dS_dt':
                        temp_df['product'] = 'grace'
                    if variable_key == 'R':
                        temp_df['product'] = 'ana river records'
                    if variable_key == 'P':
                        temp_df['product'] = 'chirps'
                    if variable_key == 'ET':
                        temp_df['product'] = 'catchment_balance:P-R-dS_dt'
                    temp_df['data'] = df.values
                    #print(temp_df)
                    #assert False
            elif 'cmip6_all_' in fname:
                if variable_key == 'dates':
                    continue
                else:
                    if variable_key == 'dates':
                        assert False
                    #assert False
                    datemin = datetime(2003, 1, 1, 0, 0)
                    datemax = datetime(2013, 12, 1, 0, 0)
                    idx = pd.date_range(datemin, datemax, freq='MS')
                    temp_df['date'] = idx
                    temp_df['catchment'] = catchment
                    temp_df['product'] = 'cmip6_' + variable_key
                    temp_df['variable'] = variable
                    temp_df['data'] = df
                    #print(temp_df)
                    #assert False
            
            elif 'cmip5_all_' in fname:
                if variable_key == 'dates':
                    continue
                else:
                    datemin = datetime(1994, 1, 1, 0, 0)
                    datemax = datetime(2004, 12, 1, 0, 0)
                    idx = pd.date_range(datemin, datemax, freq='MS')
                    temp_df['date'] = idx
                    temp_df['catchment'] = catchment
                    temp_df['product'] = 'cmip5_' + variable_key
                    temp_df['variable'] = variable
                    temp_df['data'] = df
                    #print(temp_df)
                    #assert False

            else:
                temp_df['date'] = df.index
                temp_df['catchment'] = catchment
                temp_df['product'] = variable_key
                temp_df['variable'] = variable
                col = df.columns[0]
                temp_df['data'] = df[col].values
                #print(temp_df)

            # append temp_df to all_df
            all_df = all_df.append(temp_df, ignore_index=True)
            #print(all_df.tail(3))
print(all_df.head(5))
print(all_df.tail(5))

all_df.to_csv('~/for_hess/amazon_et_estimates_2003_2013.csv')
    



