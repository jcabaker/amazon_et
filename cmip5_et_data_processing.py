#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import iris
from cube_funcs import get_dates 
from iris.experimental.equalise_cubes import equalise_attributes
from iris.util import unify_time_units
import warnings
warnings.filterwarnings("ignore")

def read_cmip_cube(fname, constraint=None):
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
path = '/nfs/a68/gyjcab/datasets/cmip5/'

# edit to read in another variable
var = 'evspsbl'

# 13 CMIP5 models analysed in study
models = ['ACCESS1-3', 'bcc-csm1-1','BNU-ESM', 'CanESM2','CCSM4', 'CESM1-BGC', 
          'FIO-ESM', 'HadGEM2-CC', 'HadGEM2-ES', 'inmcm4',
          'IPSL-CM5A-LR', 'MPI-ESM-LR','NorESM1-M']

# loop over models, read in data and calculate mean of multiple runs
for model in models:
    constraint = None
    
    if model == 'HadGEM2-ES':
        constraint = iris.Constraint(time=lambda cell:
                                     1859 <= cell.point.year <= 2004)
    if model == 'HadGEM2-CC':
        constraint = iris.Constraint(time=lambda cell:
                                     1960 <= cell.point.year <= 2004)

    print(model)
    temp1 = temp2 = temp3 = temp4 = temp5 = temp6 = temp7 = None
    temp8 = temp9 = temp10 = temp11 = temp12 = temp13 = temp14 = None
    
    # path to historical data
    fpath = path + var + '/historical/' + model
    
    temp1 = read_cmip_cube(fpath + '/*r1i1p1_*.nc', constraint=constraint)
    
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
        temp7 = read_cmip_cube(fpath + '/*r7i1p1*.nc', constraint=constraint)
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
        temp14 = read_cmip_cube(fpath + '/*r114i1p1*.nc', constraint=constraint)
    except OSError:
        pass
    
    temp_list = [temp1, temp2, temp3, temp4, temp5, temp6, temp7, temp8, temp9,
                 temp10, temp11, temp12, temp13, temp14]
    
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
    

