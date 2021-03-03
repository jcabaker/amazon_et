# Scripts for processing satellite, reanalysis and climate data

Author: Jess Baker (j.c.baker@leeds.ac.uk)

The scripts for processing the raw data used in the following paper:

Baker, J.C.A., Garcia-Carreras, L., Buermann, W., Marsham, J.H., Gloor, M., Sun, L. & Spracklen, D.V. In review. Evapotranspiration in the Amazon: spatial patterns, seasonality and recent trends in observations, reanalysis and CMIP models.

List of scripts (to be added).

Sequence for MODIS ET scripts

1. modis_et_make_dirs.sh  # this bash script sorts modis raw data into directories by year and day of year
2. modis_et_hdf2tiff_merge.sh  # this bash script calls modis_et_merge (must change path to this in modis_et_hdf2tiff_merge.py), modis_et_merge in turn calls modis_et_update_tif.py so this must be in the same directory
3. modis_et_final_processing.py  # this python script loops over files from each year, and for each 8-day file adds date, converts units, converts to monthly data
4. harmonise_modis_et.py  # this script harmonises MODIS ET data to single data cube of desired resolution
