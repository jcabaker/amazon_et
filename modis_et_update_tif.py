#!/usr/bin/python2
# -*- coding: utf-8 -*-
# python script called in modis_merge_updated
import sys
import gdal
import numpy as np
gt = sys.argv[1]
g = gdal.Open(gt)
b = g.GetRasterBand(1)
a = b.ReadAsArray()
[c, r] = a.shape
a[a > 3275] = -9999
d = gdal.GetDriverByName("GTiff")
o = d.Create(gt, r, c, 1, gdal.GDT_Float32)
o.SetGeoTransform(g.GetGeoTransform())
o.SetProjection(g.GetProjection())
o.GetRasterBand(1).WriteArray(a)
o.GetRasterBand(1).SetNoDataValue(-9999)
o.FlushCache()
