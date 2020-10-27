
import os

import rasterio
import rasterio.mask
from rasterio.features import rasterize

import geopandas as gpd
from shapely.geometry import Polygon
from shapely.ops import cascaded_union

import numpy as np
import matplotlib.pyplot as plt



raster_path = '/Users/marinazafiris/Desktop/Segmentation/data/103073/TEST_LC08_L1TP_103073_20140908_20170419_01_T1_B5.tif'
with rasterio.open(raster_path, "r") as src:
    raster_img = src.read()
    raster_meta = src.meta


shape_path = '/Users/marinazafiris/Desktop/Segmentation/WD2014ProjectInfo/Aug2014Fires/2014WDFiresAllEPSG3112.shp'
train_df = gpd.read_file(shape_path)
train_df = train_df.to_crs("EPSG:32653")

print("CRS Raster: {}, CRS Vector: {}".format(train_df.crs, src.crs))

# rasterize works with polygons that are in image coordinate system

def poly_from_utm(polygon, transform):
    poly_pts = []
    
    # make a polygon from multipolygon
    poly = cascaded_union(polygon)
    for i in np.array(poly.exterior.coords):
        
        # transfrom polygon to image crs, using raster meta
        poly_pts.append(~transform * tuple(i))
        
    # make a shapely Polygon object
    new_poly = Polygon(poly_pts)
    return new_poly

# creating binary mask for field/not_filed segmentation.

poly_shp = []
im_size = (src.meta['height'], src.meta['width'])
for num, row in train_df.iterrows():
    if row['geometry'].geom_type == 'Polygon':
        poly = poly_from_utm(row['geometry'], src.meta['transform'])
        poly_shp.append(poly)
    else:
        for p in row['geometry']:
            poly = poly_from_utm(p, src.meta['transform'])
            poly_shp.append(poly)

mask = rasterize(shapes=poly_shp, out_shape=im_size)

# plotting the mask

plt.figure(figsize=(15,15))
plt.imshow(mask)







