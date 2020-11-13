#!/usr/bin/python2
# -*- coding: utf-8 -*-
import sys
import gdal
import numpy as np
gt = sys.argv[1]
g = gdal.Open(gt)
b = g.GetRasterBand(1)
a = b.ReadAsArray()
[c, r] = a.shape
a[a > 248] = 255
d = gdal.GetDriverByName("GTiff")
o = d.Create(gt, r, c, 1, gdal.GDT_Byte)
o.SetGeoTransform(g.GetGeoTransform())
o.SetProjection(g.GetProjection())
o.SetProjection(g.GetProjection())
o.GetRasterBand(1).WriteArray(a)
o.GetRasterBand(1).SetNoDataValue(255)
o.FlushCache()
