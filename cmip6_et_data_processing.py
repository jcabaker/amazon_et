#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  3 16:15:39 2018

Convert CMIP model realizations to ensemble mean

@author: earjba
"""

import iris
from cube_funcs import get_dates 
from iris.experimental.equalise_cubes import equalise_attributes
from iris.util import unify_time_units
import warnings
warnings.filterwarnings("ignore")

def read_cmip_cube(fname, constraint=None):
    #print(fname)
    try:
        cube = iris.load_cube(fname, constraint=constraint)
    except:
        cubes = iris.load(fname, constraints=constraint)
        equalise_attributes(cubes)
        unify_time_units(cubes)
        try:
            cube = cubes.merge_cube()
        except:
            cube = cubes.concatenate_cube()
    print(cube.shape)
    return(cube)
    
    
def iris_read(data_path, standard_name, short_name=None):
    cubes = iris.load(data_path, standard_name)
    if short_name is not None:
        var_name_temp = iris.Constraint(cube_func=lambda cube:
                                        cube.var_name == short_name)
        cubes = cubes.extract(var_name_temp)
    return(cubes)

    
#%%
# change path to location of data
# data should be sorted into folders by model name
path = '/nfs/see-fs-02_users/earjba/b0122/cmip6/'

# edit to read in another variable
var = 'evspsbl'

# 10 CMIP6 models analysed in study
models = ['ACCESS-ESM1-5', 'BCC-CSM2-MR', 'BCC-ESM1',
          'CESM2', 'CESM2-WACCM', 'GISS-E2-1-G', 'HadGEM3-GC31-LL',
          'HadGEM3-GC31-MM', 'SAM0-UNICON', 'UKESM1-0-LL']

# loop over models, read in data and calculate mean of multiple runs
for model in models:
    constraint = iris.Constraint(time=lambda cell:
                                 1850 <= cell.point.year <= 2014)

    print(model)
    temp1 = temp2 = temp3 = temp4 = temp5 = temp6 = temp7 = None
    temp8 = temp9 = temp10 = temp11 = temp12 = temp13 = temp14 = None
    temp15 = temp16 = temp17 = temp18 = temp19 = temp20 = None
    
    # path to historical data
    fpath = path + var + '/historical/' + model
    
    try:
        temp1 = read_cmip_cube(fpath + '/*r1i1p1f*.nc', constraint=constraint)
    except OSError:
        pass

    try:
        temp2 = read_cmip_cube(fpath + '/*r2i1p1*.nc', constraint=constraint)
    except OSError:
        pass

    try:
        temp3 = read_cmip_cube(fpath + '/*r3i1p1*.nc', constraint=constraint)
    except OSError:
        pass

    try:
        temp4 = read_cmip_cube(fpath + '/*r4i1p1*.nc', constraint=constraint)
    except OSError:
        pass

    try:
        temp5 = read_cmip_cube(fpath + '/*r5i1p1*.nc', constraint=constraint)
    except OSError:
        pass

    try:
        temp6 = read_cmip_cube(fpath + '/*r6i1p1*.nc', constraint=constraint)
    except OSError:
        pass

    try:
        temp7= read_cmip_cube(fpath + '/*r7i1p1*.nc', constraint=constraint)
    except OSError:
        pass

    try:
        temp8 = read_cmip_cube(fpath + '/*r8i1p1*.nc', constraint=constraint)
    except OSError:
        pass

    try:
        temp9 = read_cmip_cube(fpath + '/*r9i1p1*.nc', constraint=constraint)
    except OSError:
        pass

    try:
        temp10 = read_cmip_cube(fpath + '/*r10i1p1*.nc', constraint=constraint)
    except OSError:
        pass

    try:
        temp11 = read_cmip_cube(fpath + '/*r11i1p1*.nc', constraint=constraint)
    except OSError:
        pass

    try:
        temp12 = read_cmip_cube(fpath + '/*r12i1p1*.nc', constraint=constraint)
    except OSError:
        pass

    try:
        temp13 = read_cmip_cube(fpath + '/*r13i1p1*.nc', constraint=constraint)
    except OSError:
        pass

    try:
        temp14 = read_cmip_cube(fpath + '/*r14i1p1*.nc', constraint=constraint)
    except OSError:
        pass

    try:
        temp15 = read_cmip_cube(fpath + '/*r15i1p1*.nc', constraint=constraint)
    except OSError:
        pass

    try:
        temp16 = read_cmip_cube(fpath + '/*r16i1p1*.nc', constraint=constraint)
    except OSError:
        pass

    try:
        temp17 = read_cmip_cube(fpath + '/*r17i1p1*.nc', constraint=constraint)
    except OSError:
        pass
    try:
        temp18 = read_cmip_cube(fpath + '/*r18i1p1*.nc', constraint=constraint)
    except OSError:
        pass

    try:
        temp19= read_cmip_cube(fpath + '/*r19i1p1*.nc', constraint=constraint)
    except OSError:
        pass
    
    
    temp_list = [temp1, temp2, temp3, temp4, temp5, temp6, temp7, temp8, temp9,
                 temp10, temp11, temp12, temp13, temp14, temp15, temp16, temp17,
                 temp18, temp19, temp20]
    
    # get list of model runs
    temp_list_trim = [x for x in temp_list if x is not None]
    print(len(temp_list_trim))
    
    # if length only 1 save as new netcdf
    if len(temp_list_trim) == 1:
        ensemble_mean = temp_list_trim[0]
        ensemble_mean.standard_name = temp_list_trim[0].standard_name
        ensemble_mean.attributes = temp_list_trim[0].attributes
        dates = get_dates(ensemble_mean, verbose=False)
        outpath = (fpath + '/test_ensemble_mean_historical_' +
                   model + '_' + var + '_' +
                   str(dates[0].year) + str(dates[0].month).zfill(2) + '_' +
                   str(dates[-1].year) + str(dates[-1].month).zfill(2) + '.nc')
        print(outpath)          
        iris.save(ensemble_mean, outpath)
        continue
        
    else:
        # if multiple runs calculate mean of runs
        n = len(temp_list_trim)
        print(n)
        equalise_attributes(temp_list_trim)
        unify_time_units(temp_list_trim)
        if n == 2:
            ensemble_mean = (temp_list_trim[0] + temp_list_trim[1])/n
            
        if n == 3:
            ensemble_mean = (temp_list_trim[0] + temp_list_trim[1] +
                             temp_list_trim[2])/n
        if n == 4:
           ensemble_mean = (temp_list_trim[0] + temp_list_trim[1] +
                                 temp_list_trim[2] + temp_list_trim[3])/n
        if n == 5:
            ensemble_mean = (temp_list_trim[0] + temp_list_trim[1] +
                             temp_list_trim[2] + temp_list_trim[3] +
                             temp_list_trim[4])/n
        if n == 6:
            ensemble_mean = (temp_list_trim[0] + temp_list_trim[1] +
                             temp_list_trim[2] + temp_list_trim[3] +
                             temp_list_trim[4] + temp_list_trim[5])/n
      
        if n == 7:
            ensemble_mean = (temp_list_trim[0] + temp_list_trim[1] +
                             temp_list_trim[2] + temp_list_trim[3] +
                             temp_list_trim[4] + temp_list_trim[5] +
                             temp_list_trim[6])/n
                             
        if n == 8:
            ensemble_mean = (temp_list_trim[0] + temp_list_trim[1] +
                             temp_list_trim[2] + temp_list_trim[3] +
                             temp_list_trim[4] + temp_list_trim[5] +
                             temp_list_trim[6] + temp_list_trim[7])/n
        
        if n == 9:
            ensemble_mean = (temp_list_trim[0] + temp_list_trim[1] +
                             temp_list_trim[2] + temp_list_trim[3] +
                             temp_list_trim[4] + temp_list_trim[5] +
                             temp_list_trim[6] + temp_list_trim[7] +
                             temp_list_trim[8])/n
            
        if n == 10:
            ensemble_mean = (temp_list_trim[0] + temp_list_trim[1] +
                             temp_list_trim[2] + temp_list_trim[3] +
                             temp_list_trim[4] + temp_list_trim[5] +
                             temp_list_trim[6] + temp_list_trim[7] +
                             temp_list_trim[8] + temp_list_trim[9])/n
        
        if n == 11:
            if model == 'CESM2':  # members 8, 9 and 10 lat match error error
                ensemble_mean = (temp_list_trim[0] + temp_list_trim[1] +
                                 temp_list_trim[2] + temp_list_trim[3] +
                                 temp_list_trim[4] + temp_list_trim[5] +
                                 temp_list_trim[6] + temp_list_trim[7])/(n-3)
            else:
                ensemble_mean = (temp_list_trim[0] + temp_list_trim[1] +
                                 temp_list_trim[2] + temp_list_trim[3] +
                                 temp_list_trim[4] + temp_list_trim[5] +
                                 temp_list_trim[6] + temp_list_trim[7] +
                                 temp_list_trim[8] + temp_list_trim[9] +
                                 temp_list_trim[10])/n


        if n == 12:
            ensemble_mean = (temp_list_trim[0] + temp_list_trim[1] +
                             temp_list_trim[2] + temp_list_trim[3] +
                             temp_list_trim[4] + temp_list_trim[5] +
                             temp_list_trim[6] + temp_list_trim[7] +
                             temp_list_trim[8] + temp_list_trim[9] +
                             temp_list_trim[10] + temp_list_trim[11])/n
            
        if n == 13:
            ensemble_mean = (temp_list_trim[0] + temp_list_trim[1] +
                             temp_list_trim[2] + temp_list_trim[3] +
                             temp_list_trim[4] + temp_list_trim[5] +
                             temp_list_trim[6] + temp_list_trim[7] +
                             temp_list_trim[8] + temp_list_trim[9] +
                             temp_list_trim[10] + temp_list_trim[11] +
                             temp_list_trim[12])/n
        
        if n == 14:
            ensemble_mean = (temp_list_trim[0] + temp_list_trim[1] +
                             temp_list_trim[2] + temp_list_trim[3] +
                             temp_list_trim[4] + temp_list_trim[5] +
                             temp_list_trim[6] + temp_list_trim[7] +
                             temp_list_trim[8] + temp_list_trim[9] +
                             temp_list_trim[10] + temp_list_trim[11] +
                             temp_list_trim[12] + temp_list_trim[13])/n

        if n == 15:
            ensemble_mean = (temp_list_trim[0] + temp_list_trim[1] +
                             temp_list_trim[2] + temp_list_trim[3] +
                             temp_list_trim[4] + temp_list_trim[5] +
                             temp_list_trim[6] + temp_list_trim[7] +
                             temp_list_trim[8] + temp_list_trim[9] +
                             temp_list_trim[10] + temp_list_trim[11] +
                             temp_list_trim[12] + temp_list_trim[13] +
                             temp_list_trim[14])/n

        if n == 16:
            ensemble_mean = (temp_list_trim[0] + temp_list_trim[1] +
                             temp_list_trim[2] + temp_list_trim[3] +
                             temp_list_trim[4] + temp_list_trim[5] +
                             temp_list_trim[6] + temp_list_trim[7] +
                             temp_list_trim[8] + temp_list_trim[9] +
                             temp_list_trim[10] + temp_list_trim[11] +
                             temp_list_trim[12] + temp_list_trim[13] +
                             temp_list_trim[14] + temp_list_trim[15])/n

        if n == 17:
            ensemble_mean = (temp_list_trim[0] + temp_list_trim[1] +
                             temp_list_trim[2] + temp_list_trim[3] +
                             temp_list_trim[4] + temp_list_trim[5] +
                             temp_list_trim[6] + temp_list_trim[7] +
                             temp_list_trim[8] + temp_list_trim[9] +
                             temp_list_trim[10] + temp_list_trim[11] +
                             temp_list_trim[12] + temp_list_trim[13] +
                             temp_list_trim[14] + temp_list_trim[15] + 
                             temp_list_trim[16])/n

        if n == 18:
            ensemble_mean = (temp_list_trim[0] + temp_list_trim[1] +
                             temp_list_trim[2] + temp_list_trim[3] +
                             temp_list_trim[4] + temp_list_trim[5] +
                             temp_list_trim[6] + temp_list_trim[7] +
                             temp_list_trim[8] + temp_list_trim[9] +
                             temp_list_trim[10] + temp_list_trim[11] +
                             temp_list_trim[12] + temp_list_trim[13] +
                             temp_list_trim[14] + temp_list_trim[15] + 
                             temp_list_trim[16] + temp_list_trim[17])/n

        if n == 19:
            ensemble_mean = (temp_list_trim[0] + temp_list_trim[1] +
                             temp_list_trim[2] + temp_list_trim[3] +
                             temp_list_trim[4] + temp_list_trim[5] +
                             temp_list_trim[6] + temp_list_trim[7] +
                             temp_list_trim[8] + temp_list_trim[9] +
                             temp_list_trim[10] + temp_list_trim[11] +
                             temp_list_trim[12] + temp_list_trim[13] +
                             temp_list_trim[14] + temp_list_trim[15] +
                             temp_list_trim[16] + temp_list_trim[17] + 
                             temp_list_trim[18])/n
        
        if n == 20:
            ensemble_mean = (temp_list_trim[0] + temp_list_trim[1] +
                             temp_list_trim[2] + temp_list_trim[3] +
                             temp_list_trim[4] + temp_list_trim[5] +
                             temp_list_trim[6] + temp_list_trim[7] +
                             temp_list_trim[8] + temp_list_trim[9] +
                             temp_list_trim[10] + temp_list_trim[11] +
                             temp_list_trim[12] + temp_list_trim[13] +
                             temp_list_trim[14] + temp_list_trim[15] +
                             temp_list_trim[16] + temp_list_trim[17] +
                             temp_list_trim[18] + temp_list_trim[19])/n
                             
        # save as new netcdf 
        ensemble_mean.standard_name = temp_list_trim[0].standard_name
        ensemble_mean.attributes = temp_list_trim[0].attributes
        dates = get_dates(ensemble_mean, verbose=False)
        outpath = (fpath + '/test_ensemble_mean_historical_' +
                   model + '_' + var + '_' +
                   str(dates[0].year) + str(dates[0].month).zfill(2) + '_' +
                   str(dates[-1].year) + str(dates[-1].month).zfill(2) + '.nc')
        print(outpath)          
        iris.save(ensemble_mean, outpath)
    

