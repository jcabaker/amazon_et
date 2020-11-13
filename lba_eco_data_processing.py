import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def read_lba_flux_data(path, folder_name):

    fid = '_Avg_month_qaqc.csv'
    fpath = path + folder_name + '/' + folder_name[-8:-5] + fid
    data = pd.read_csv(fpath)
    data = data.dropna()
    data.columns = data.iloc[0]
    data = data.iloc[1:]
    data = data.reset_index()
    ### generate dates from year and doy
    dates = []
    for i in range(len(data)):
        year = data.year.iloc[i]
        days = data.day.iloc[i]
        dates.append(datetime(int(year), 1, 1) +
                     timedelta(int(days) - 1))
    data['dates'] = dates
    data_trim = data[['dates','LE', 'prec']].copy()

    ### convert LE col from string to float
    data_trim['LE'] = pd.to_numeric(data_trim['LE'], errors='coerce').fillna(0)

    ### convert LE to ET
    lhv = 2.501e6
    data_trim['ET'] = (data_trim['LE']/lhv) * 60*60*24*30.5
    i, = np.where(data_trim.ET < 0)
    data_trim.loc[i, 'ET'] = np.nan
    #print(data_trim.head(5))
    return(data_trim)


# read in quality-controlled flux data
# path to QAQC data
path = ('/nfs/a68/gyjcab/datasets/brazil_flux_data/LBA_data/'
        'CD32_BRAZIL_FLUX_NETWORK_1174/data/')

# read data for ban, k34, k67, k83, rja, pdg
ban = read_lba_flux_data(path,'TOC_BAN_QAQC')
k34 = read_lba_flux_data(path,'MAN_K34_QAQC')
k67 = read_lba_flux_data(path,'STM_K67_QAQC')
k83 = read_lba_flux_data(path,'STM_K83_QAQC')
rja = read_lba_flux_data(path,'RON_RJA_QAQC')
pdg = read_lba_flux_data(path,'SP_PDG_QAQC')


