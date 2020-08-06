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

# define the file names for RGB and panchromatic (pan) images
def read_files(ID):
    
    file_rgb = "./data/"+ID+"/"+ID+"_RGB.tif"
    file_pan = "./data/"+ID+"/"+ID+"_B8.tif"
    file_qa = "./data/"+ID+"/"+ID+"_BQA.tif"
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
    qa = data_qa.GetRasterBand(1).ReadAsArray().astype(float)
    
    # max pixel to normalize values
    max_pix = np.max(rgb) #np.max(array_rgb)

    # normalize RGB and pan
    array_rgb = rgb / max_pix
    array_pan = pan / max_pix

    # must resize in order to replace value later
    columns = data_pan.RasterXSize
    rows = data_pan.RasterYSize
    array_rgb = resize(array_rgb, (rows, columns))
    array_qa = qa
    return array_rgb, array_pan, array_qa

def random_subset(array_qa, x, y):
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
    
    # Array bounds x1, x2, y1, y2 transformed to meet MS transformation
    x1, x2, y1, y2 = 2*x1, 2*x2, 2*y1, 2*y2
    print("done sub")
    return x1, x2, y1, y2

def rgb_pan(array_rgb, array_pan, x1, x2, y1, y2):
    # Subsetting 
    sub_array_rgb = array_rgb[x1:x2, y1:y2, :]
    sub_array_pan = array_pan[x1:x2, y1:y2]
    # HSV to RGB transform
    array_hsv = rgb2hsv(sub_array_rgb)
    # Replacing value with pan
    array_hsv[:, :, 2] = sub_array_pan
    # Converting back to RGB
    pansharpend_rgb = hsv2rgb(array_hsv)
    print("done pan")
    return pansharpend_rgb


# Amazon Scene ID Directory
s3_scenes = pd.read_csv('http://landsat-pds.s3.amazonaws.com/c1/L8/scene_list.gz', compression='gzip')

# Filtering for our specified scene
aus_desert = s3_scenes[(s3_scenes['productId'].str[:16].str.contains('LC08_L1TP_109076')) & (s3_scenes['cloudCover'] < 10)]

n = 5 #Number of Sample images wanting to create

chosen_idx = np.random.choice(len(aus_desert), replace = True, size = n)

sample = aus_desert.iloc[chosen_idx]

# Dimensions of Wanted Images
x = 500
y = 500

for index, row in sample.iterrows():
    
    # ID is also the name of given image folder
    ID = row.productId
    
    array_rgb, array_pan, array_qa = read_files(ID)
    print(ID+": Done read_files")
    
    x1, x2, y1, y2 = random_subset(array_qa, x, y)
    print(ID+": Done random_subset")
    
    pansharpend_rgb = rgb_pan(array_rgb, array_pan, x1, x2, y1, y2)
    print(ID+": Done rgb_pan")
    
    file_name = ID+"_"+str(x1)+"_"+str(x2)+"_"+str(y1)+"_"+str(y2)+".jpg"
    imsave(fname=file_name, arr=pansharpend_rgb)
    print(file_name+"  created")
