# Necessary Packages
import pandas as pd
import random

# needed to open GeoTIFF files
from osgeo import gdal
from gdalconst import *
import matplotlib.pyplot as plt
import numpy as np

# resize raster, and do HSV to RGB transformations
from skimage.transform import resize
from skimage.color import rgb2hsv, hsv2rgb
from skimage.io import imsave

# Defines the file names for RGB and panchromatic (pan) images and creates arrays
def read_files(ID, path):
    
    file_rgb = path + "/" + ID + "_RGB.tif"
    file_pan = path + "/" + ID + "_B8.tif"
    file_qa = path + "/" + ID + "_BQA.tif"
    # load the data
    try:
        data_rgb = gdal.Open(file_rgb, GA_ReadOnly)
        data_pan = gdal.Open(file_pan, GA_ReadOnly) 
        data_qa = gdal.Open(file_qa, GA_ReadOnly) 
    except:
        print('error loading files')
    
    # Initialize empty RGB array
    columns = data_rgb.RasterXSize
    rows = data_rgb.RasterYSize
    rgb = np.zeros((rows, columns, 3))

    # Fill arrays from TIFs
    rgb[:,:,0] = data_rgb.GetRasterBand(3).ReadAsArray().astype(float)
    rgb[:,:,1] = data_rgb.GetRasterBand(2).ReadAsArray().astype(float)
    rgb[:,:,2] = data_rgb.GetRasterBand(1).ReadAsArray().astype(float)
    pan = data_pan.GetRasterBand(1).ReadAsArray().astype(float)
    array_qa = data_qa.GetRasterBand(1).ReadAsArray().astype(float)
    
    return rgb, pan, array_qa

# Checks the QA subset for approved pixel values, subsets RGB, transforms bounds, subsets Pan
def qa_check_sub(array_qa, x, y, rgb, pan):
    
    # Creating buffer zone so we never pick up a number that would force us out of bounds
    high_x = array_qa.shape[1]-x 
    high_y = array_qa.shape[0]-y
    
    # Selecting random subset
    x1 = np.random.randint(0, high=high_x, size=None, dtype='l')
    x2 = x1+x
    y1 = np.random.randint(0, high=high_y, size=None, dtype='l')
    y2 = y1+y
    sub_array_qa = array_qa[x1:x2, y1:y2]
    
    # Unique pixel values
    values_qa = list(np.sort(np.unique(sub_array_qa)))
    
    # Checks that above pixel values in subset pass QA check of values we want
    
    values_approved = [2720.0]
    l = list(filter(lambda num: (num not in values_approved), values_qa))
    
    # Will repeat above steps until approved subset is found
    while len(l) > 0:
        x1 = np.random.randint(0, high=high_x, size=None, dtype='l')
        x2 = x1+x
        y1 = np.random.randint(0, high=high_y, size=None, dtype='l')
        y2 = y1+y
        sub_array_qa = array_qa[x1:x2, y1:y2]
        values_qa = list(np.sort(np.unique(sub_array_qa)))
        l = list(filter(lambda num: (num not in values_approved), values_qa))
    
    # Subsetting RGB before transformation
    array_rgb = rgb[x1:x2, y1:y2]
    
    # Array bounds x1, x2, y1, y2 transformed to meet Pan Subset
    x1, x2, y1, y2 = 2*x1, 2*x2, 2*y1, 2*y2
    
    # Subsetting Pan
    array_pan = pan[x1:x2, y1:y2]
    
    return array_rgb, array_pan, x1, x2, y1, y2

# Normalizes RGB and Pan subsets, resizes RGB subset to fit Pan
def transform_rgb(array_rgb, array_pan):

    # max pixel to normalize values
    max_pix = np.max(array_rgb)

    # normalize RGB and pan
    array_rgb = array_rgb / max_pix
    array_pan = array_pan / max_pix

    # must resize in order to replace value later
    columns = array_pan.shape[1]
    rows = array_pan.shape[0]
    array_rgb = resize(array_rgb, (rows, columns))
    
    return array_rgb, array_pan

# RGB to HSV transformation, to replace value with pan band
def pansharpening(array_rgb, array_pan):

    # RGB to HSV transformation
    array_hsv = rgb2hsv(array_rgb)
    
    # Replacing "value" with pan subset
    array_hsv[:, :, 2] = array_pan
    
    # Converting back to RGB
    pansharpend_rgb = hsv2rgb(array_hsv)
    
    return pansharpend_rgb



# Amazon Scene ID Directory
s3_scenes = pd.read_csv('http://landsat-pds.s3.amazonaws.com/c1/L8/scene_list.gz', compression='gzip')

# Filtering for our specified scene
aus_desert = s3_scenes[(s3_scenes['productId'].str[:16].str.contains('LC08_L1TP_109076')) & (s3_scenes['cloudCover'] < 10)]

n = 5 # Number of Sample images wanting to create

chosen_idx = np.random.choice(len(aus_desert), replace = True, size = n)

sample = aus_desert.iloc[chosen_idx] 

# Dimensions of Wanted Images
x = 500
y = 500

for index, row in sample.iterrows():
    
    # ID is also the name of given image folder
    ID = row.productId
    path = "./data/"+ID
    
    rgb, pan, array_qa = read_files(ID, path)
    print(ID+": Done read_files")
    
    array_rgb, array_pan, x1, x2, y1, y2 = qa_check_sub(array_qa, x, y, rgb, pan)
    print(ID+": Done qa_check_sub")
    
    array_rgb, array_pan = transform_rgb(array_rgb, array_pan)
    print(ID+": Done transform_rgb")
    
    pansharpend_rgb = pansharpening(array_rgb, array_pan)
    print(ID+": Done pansharpening")
    
    file_name = ID+"_"+str(x1)+"_"+str(x2)+"_"+str(y1)+"_"+str(y2)+".jpg"
    imsave(fname=file_name, arr=pansharpend_rgb)
    print(file_name+"  created")
