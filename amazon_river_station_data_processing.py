#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sunday 16 May 2020

@author: earjba
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import chardet
import statsmodels.formula.api as smf
  
    
def substring_after(s, delim):
    return(s.partition(delim)[0])
    

def plot(df1, df2, col='blue', xlabel='X', ylabel='Y'):
    """ Function to make plot of regression relationship between two dfs"""

    # Find where both dfs have values and put aligned data in new df
    datemin = max(df1.index[0], df2.index[0])
    datemax = min(df1.index[-1], df2.index[-1])

    df1_trim = df1[datemin:datemax]
    df2_trim = df2[datemin:datemax]
    mask = ~np.isnan(df1_trim.iloc[:, 0]) & ~np.isnan(df2_trim.iloc[:, 0])
    data = pd.DataFrame()
    data['x'] = df1_trim.iloc[:, 0][mask]
    data['y'] = df2_trim.iloc[:, 0][mask]

    # Set up plot
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111)

    # Perform regression
    lm = smf.ols(formula='y ~ x', data=data).fit()
    X_new = [data.x.min(), data.x.max()]
    preds = np.empty([2])
    preds[0] = (X_new[0]*lm.params[1])+lm.params[0]
    preds[1] = (X_new[1]*lm.params[1])+lm.params[0]

    # Plot data
    ax.scatter(data.x, data.y, color=col, s=2)
    minlim = round(min(min(data.x), min(data.y)) -
                   0.05*min(min(data.x), min(data.y)))
    maxlim = round(max(max(data.x), max(data.y)) -
                   0.05*max(max(data.x), max(data.y)))
    ax.set_xlim(minlim, maxlim)
    ax.set_ylim(minlim, maxlim)
    ax.set_xlabel(xlabel, fontsize=14)
    ax.set_ylabel(ylabel, fontsize=14)

    # Plot regression and 1:1 line
    if lm.pvalues[1] <= 0.05:
        ax.plot(X_new, preds[0:2], color=col, linewidth=1)
        ax.plot((minlim, maxlim), (minlim, maxlim), ls='--', color='k', lw=0.8)
    
    # Annotate plot
    m = round(lm.params[1], 4)
    c = round(lm.params[0], 1)
    txt = 'R$^{2}$ = '+str(round(lm.rsquared, 2))
    txt2 = 'y = ' +  str(m) + 'x + ' + str(c)
    x1 = minlim + (maxlim-minlim)*0.05
    y1 = maxlim - (maxlim-minlim)*0.075
    y2 = y1 - (maxlim-minlim)*0.05
    plt.text(x1, y1, txt, color=col, fontsize=14)
    plt.text(x1, y2 , txt2, color=col, fontsize=14)
    return(m, c)
    

def sort_river_data(df, val='Media', basin_name=None):

    df.Data = pd.to_datetime(df.Data, format='%d/%m/%Y')
    df = df.sort_values(by=['Data'],ascending=[True])
    df = df.set_index('Data')
    j = np.where(df.columns == val)
    df_trim = pd.DataFrame(data=df,columns=df.columns[j],copy=True)
    df_trim[val] = df_trim[val].str.replace(',', '.')
    df_trim[val] = pd.to_numeric(df_trim[val]).fillna(0)
    i, = np.where(df_trim[val]==0)
    df_trim[val][i] = np.nan
    print(df_trim.tail(5))
    return(df_trim)
#%%
# Set path to river data
# Change path to data
riv_path = '/Users/jess/Documents/river_data/'

filedirs = ['Aripuana_Prainha_Velha_15830000',
             'Japura_Villa_Bittencourt_12845000',
             'Madeira_Porto_Velho_15400000',
             'Purus_Labrea_13870000',
             'Tapajos_Itaituba_17730000',  
             'Branco_Caracarai_14710000',
             'Jari_Sao_Francisco_19150000',
             'Negro_Serrinha_14420000',
             'Solimoes_Sao_Paulo_de_Olivenca_11400000',
             'Xingu_Altamira_18850000',
             'Amazon_Obidos_17050001']


filenames = []
for fdir in filedirs:
    code = fdir.split('_')[-1]
    temp = '/vazoes_C_' + code + '.csv'
    filenames.append(fdir + temp)
print(filenames)

# Read river data into dictionary
riv_data = {}
for filename in filenames:
    basin = filename.split('_')[0]
    if basin == 'Tapajos':
        basin = filename.split('_')[0] + '_' + filename.split('_')[1]
        print(basin)

    with open(riv_path+filename, 'rb') as f:
        result = chardet.detect(f.read())
    temp = pd.read_csv(riv_path+filename, sep=';', encoding=result['encoding'],
                       header=0, skiprows=13, index_col=False)

    riv_data[basin] = temp

print(riv_data.keys())
#%%
# Get river data
for key in riv_data.keys():
    print(key)
    df = riv_data[key].copy()
    test = sort_river_data(df)
    print(test.head(5))
    # gap fill Itaituba Tapajos data from another station
    if key == 'Tapajos_Itaituba':
        ita = test
        ita = ita.groupby(ita.index).mean()
        
        fname = 'Tapajos_Bubure_17710000/vazoes_C_17710000.csv'
        bubure = pd.read_csv((riv_path+fname), sep=';',
                               encoding=result['encoding'],
                               header=0, skiprows=13, index_col=False)
        bub = sort_river_data(bubure)
        bub = bub.groupby(bub.index).mean()
        m, c = plot(bub, ita,
                               xlabel='Bubere river discharge (m$^{3}$)',
                               ylabel='Itaituba river discharge (m$^{3}$)')

        datemin = max(bub.index[0], ita.index[0])
        datemax = min(bub.index[-1], ita.index[-1])
    
        bub_trim = bub[datemin:datemax]
        ita_trim = ita[datemin:datemax]
    
        idx = pd.date_range(datemin, datemax, freq='MS')
        bub_trim = bub_trim.reindex(idx, fill_value=np.nan)
        ita_trim = ita_trim.reindex(idx, fill_value=np.nan)
        
        ita_trim['fill'] = ita_trim['Media']
        counter = 0
        for i in ita_trim.index:
            j = ita_trim.loc[i][0]
        #    print(np.isnan(j))
            if np.isnan(j) == True:
                fill = m*(bub_trim.loc[i][0]) + c
                print(fill)
                ita_trim.loc[i][0] = fill
                ita_trim.loc[i]['fill'] = fill
                
                if np.isnan(fill) == False:
                    counter += 1
        ita_df = test.copy()
        datemin2 = ita_df.index[0]
        datemax2 = ita_df.index[-1]
        idx = pd.date_range(datemin2, datemax2, freq='MS')
        ita_df = ita_df.reindex(idx, fill_value=np.nan)
        ita_df['fill'] = ita_df['Media']
        ita_df['fill'][datemin:datemax] = ita_trim['fill']       
        test = ita_df[['fill']]
        test.columns = ['Media']
    test = test.groupby(test.index).mean()
    
    # ensure monotonic dates
    datemin = test.index[0]
    datemax = test.index[-1]
    print(datemin, ', ', datemax)
    idx = pd.date_range(datemin, datemax, freq='MS')
    test = test.reindex(idx, fill_value=np.nan)
    plt.figure(figsize=(6,2))
    plt.plot(test)
    plt.title(key)
    test.to_csv(riv_path + key + '_flow_data_sorted_test.csv')
