# Scripts for processing satellite, reanalysis and climate data

Author: Jess Baker (j.c.baker@leeds.ac.uk)

The scripts for processing the raw data used in the following paper:

Baker, J.C.A., Garcia-Carreras, L., Buermann, W., Marsham, J.H., Gloor, M., Sun, L. & Spracklen, D.V. In review. Evapotranspiration in the Amazon: spatial patterns, seasonality and recent trends in observations, reanalysis and CMIP models.

# List of scripts

## Scripts to process raw satellite, ERA5 and CMIP model data to harmonised netcdfs
1. chirps_p_data_processing.py
2. clara-a1_radiation_data_processing.py
3. gleam_et_data_processing.py
4. grace_tws_data_processing.py
5. p-lsh_et_data_processing.py
6. era5_et_data_processing.py
7. era5_lai_high_data_processing.py
8. era5_pr_data_processing.py
9. era5_rdn_data_processing.py
10. cmip5_et_data_processing.py
11. cmip6_et_data_processing.py

##  Scripts with additional functions called during harmonisation and data processing 
1. cube_funcs.py
2. harmonise.py

## Scripts for processing 500-m sinusoidal MODIS ET tiles
1. modis_et_make_dirs.sh  # this bash script sorts modis raw data into directories by year and day of year
2. modis_et_hdf2tiff_merge.sh  # this bash script calls modis_et_merge (must change path to this in modis_et_hdf2tiff_merge.py), modis_et_merge in turn calls modis_et_update_tif.py so this must be in the same directory
3. modis_et_final_processing.py  # this python script loops over files from each year, and for each 8-day file adds date, converts units, converts to monthly data
4. harmonise_modis_et.py  # this script harmonises MODIS ET data to single data cube of desired resolution

## Script to process raw river runoff data from ANA
1. amazon_river_station_data_processing.py

## Script to process raw flux tower data from LBA
1. lba_eco_data_processing.py

## Scripts to extract basin monthly-mean values of ET, leaf area index, precipitation and radiation
1. get_catchment_balance_ET_all_basins.py --> get catchment-balance data for Amazon and sub-basins
2. get_satellite_et_all_basins_interannual.py
3. get_satellite_lai_all_basins_interannual.py
4. get_satellite_pre_all_basins_interannual.py
5. get_satellite_rdn_all_basins_interannual.py
6. get_era5_et_all_basins_interannual.py
7. get_era5_lai_high_all_basins_interannual.py
8. get_era5_pr_all_basins_interannual.py
9. get_era5_rdn_all_basins_interannual.py
10. get_cmip5_et_all_basins_interannual.py
11. get_cmip5_lai_all_basins_interannual.py
12. get_cmip5_pr_all_basins_interannual.py
13. get_cmip5_rdn_all_basins_interannual.py
10. get_cmip6_et_all_basins_interannual.py
11. get_cmip6_lai_all_basins_interannual.py
12. get_cmip6_pr_all_basins_interannual.py
13. get_cmip6_rdn_all_basins_interannual.py

## Script to collate Amazon monthly mean ET, P, RDN and LAI values
Dataset stored here: https://zenodo.org/record/4271331#.YD-emS2l30o
Amazon basin-mean monthly estimates of evapotranspiration estimated from catchment-balance analysis, satellites (MODIS, P-LSH and GLEAM), reanalysis (ERA5) and the CMIP5 and CMIP6 climate models. Catchment level estimates of climate variables that influence ET are also included (precipitation, radiation and leaf area index). Full details of all source datasets are provided in 'Evapotranspiration in the Amazon: spatial patterns, seasonality and recent trends in observations, reanalysis and CMIP models' in review in Hydrology and Earth System Sciences.
1. all_data_catchment_level.py

## Script to estimate uncertainty in Amazon catchment-balance ET
1. quantify_uncertainty_in_catchment_et.py
