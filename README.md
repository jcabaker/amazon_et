# Scripts for processing satellite, reanalysis and climate data

Author: Jess Baker (j.c.baker@leeds.ac.uk)

The scripts for processing the raw data used in the following paper:

Baker, J.C.A., Garcia-Carreras, L., Buermann, W., Marsham, J.H., Gloor, M., Sun, L. & Spracklen, D.V. In review. Evapotranspiration in the Amazon: spatial patterns, seasonality and recent trends in observations, reanalysis and CMIP models.

List of scripts (to be added).

Sequence for MODIS ET scripts

1. make_dirs_modis_et.sh  # this bash script sorts modis raw data into directories by year and day of year
2. hdf2tiff_merge_modis.sh  # this bash script calls modis_merge_updated (must change path to this in hdf2tiff_merge_modis.py), modis_merge_updated in turn calls update_modis_tif.py so this must be in the same directory
3. process_mod16a2_et_final.py  # this python script loops over files from each year, and for each 8-day file adds date, converts units, converts to monthly data
4. harmonise_modis_et_data.py  # this script harmonises MODIS Et data to single data cube of desired resolution

