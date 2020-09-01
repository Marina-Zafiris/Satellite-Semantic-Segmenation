#!/usr/bin/env python
# coding: utf-8

# In[114]:


import os, random
import pandas as pd
# needed to open GeoTIFF files
from osgeo import gdal
from gdalconst import *
import matplotlib.pyplot as plt
import numpy as np
import rasterio.features
from PIL import Image

# resize raster, and do HSV to RGB transformations
from skimage.transform import resize
from skimage.color import rgb2hsv, hsv2rgb
from skimage.io import imsave
from osgeo import ogr


# In[115]:



def read_files(path, folder, ID):
    
    file_b = path + "/" + folder + "/" + ID + "_B2.tif" #Blue
    tif_b = Image.open(file_b)
    array_b = np.array(tif_b)
    
    file_g = path + "/" + folder + "/" + ID + "_B3.tif" #Green
    tif_g = Image.open(file_g)
    array_g = np.array(tif_g)
    
    file_r = path + "/" + folder + "/" + ID + "_B4.tif" #Red
    tif_r = Image.open(file_r)
    array_r = np.array(tif_r)
    
    file_nir = path + "/" + folder + "/" + ID + "_B5.tif" #Near Infrared
    tif_nir = Image.open(file_nir)
    array_nir = np.array(tif_nir)
    
    file_qa = path + "/" + folder + "/" + ID + "_BQA.tif" #Quality Assesment  
    tif_qa = Image.open(file_qa)
    array_qa = np.array(tif_qa)
    
    # Have to use GDAL because its big
    file_gt = path + "/" + folder + "/" + ID + "_GT.tif" #Ground Truth 
    tif_gt = Image.open(file_gt)
    array_gt = np.array(tif_gt, dtype = int)
    # fills array gt
    rows = array_b.shape[0]-array_gt.shape[0]
    row_fill = np.zeros((rows, array_gt.shape[1]), dtype=int)
    array_gt = np.append(array_gt, row_fill , axis=0)
    cols = array_b.shape[1]-array_gt.shape[1]
    cols_fill = np.zeros((array_gt.shape[0], cols), dtype=int)
    array_gt = np.append(array_gt, cols_fill , axis=1)
    #tif_gt = gdal.Open(file_gt, GA_ReadOnly)
    #array_gt = tif_gt.GetRasterBand(1).ReadAsArray().astype(int)
    
    # Have to use GDAL because its big
    #file_pan = path + "/" + folder + "/" + ID + "_B8.tif" #Pan
    #tif_pan = gdal.Open(file_pan, GA_ReadOnly)
    #array_pan = tif_pan.GetRasterBand(1).ReadAsArray().astype(float)
    
    return array_b, array_g, array_r, array_nir, array_qa, array_gt


# In[116]:


#103073_MS = (7795, 7602)
def qa_check_sub(x, y, array_b, array_g, array_r, array_nir, array_qa, array_gt):
    
    values_approved = [2720.0]
    l = [0]
    
    if folder == str(103073):     
        while len(l) > 0:
            x2 = np.random.randint(x, high=5017, size=None, dtype='l')
            x1 = x2-x
            y2 = np.random.randint(3898, high=7795-y, size=None, dtype='l')
            y1 = y2-y
            sub_array_qa = array_qa[x1:x2, y1:y2]
            values_qa = list(np.sort(np.unique(sub_array_qa)))
            l = list(filter(lambda num: (num not in values_approved), values_qa))
    
    if folder == str(103074):
        while len(l) > 0:
            x2 = np.random.randint(x, high=3801, size=None, dtype='l')
            x1 = x2-x
            y2 = np.random.randint(y, high=2595, size=None, dtype='l')
            y1 = y2-y
            sub_array_qa = array_qa[x1:x2, y1:y2]
            values_qa = list(np.sort(np.unique(sub_array_qa)))
            l = list(filter(lambda num: (num not in values_approved), values_qa))
    
    if folder == str(104073):
        while len(l) > 0:
            x1 = np.random.randint(3801, high=7602-x, size=None, dtype='l')
            x2 = x1+x
            y1 = np.random.randint(2595, high=7795-y, size=None, dtype='l')
            y2 = y1+y
            sub_array_qa = array_qa[x1:x2, y1:y2]
            values_qa = list(np.sort(np.unique(sub_array_qa)))
            l = list(filter(lambda num: (num not in values_approved), values_qa))

    # Subsetting RGB and NIR
    sub_b = array_b[x1:x2, y1:y2]
    sub_g = array_g[x1:x2, y1:y2]
    sub_r = array_r[x1:x2, y1:y2]
    sub_nir = array_nir[x1:x2, y1:y2]
    sub_gt = array_gt[x1:x2, y1:y2]
    
    # Array bounds x1, x2, y1, y2 transformed to meet Pan Subset
    #x1, x2, y1, y2 = 2*x1, 2*x2, 2*y1, 2*y2
    
    # Subsetting Pan
    #sub_pan = array_pan[x1:x2, y1:y2]
    
    return sub_b, sub_g, sub_r, sub_nir, sub_gt, x1, x2, y1, y2


# In[110]:


aus_desert = pd.read_csv("Australian_Desert_Scenes.csv", index_col='Unnamed: 0')

row = ['103074']

path = "./data"

x = 384
y = 384

array_b, array_g, array_r, array_nir, array_qa, array_gt = read_files(path, folder, ID)
sub_b, sub_g, sub_r, sub_nir, sub_gt, x1, x2, y1, y2 = qa_check_sub(x, y, array_b, array_g, array_r, array_nir, array_qa, array_gt)


# In[111]:


np.unique(sub_gt)


# In[9]:


def transform_subs(sub_b, sub_g, sub_r, sub_nir, sub_gt, sub_pan):
    # Create RBG
    sub_rgb = np.stack((sub_r, sub_g, sub_b),2)
    
    # max pixel to normalize values
    max_pix = np.max(sub_rgb)

    # normalize RGB and pan
    sub_rgb = sub_rgb / max_pix
    sub_pan = sub_pan / max_pix

    # must resize in order to replace value later
    columns = sub_pan.shape[1]
    rows = sub_pan.shape[0]
    sub_rgb = resize(sub_rgb, (rows, columns))
    sub_nir = resize(sub_nir, (rows, columns))
    sub_gt = resize(sub_gt, (rows, columns))
    
    return sub_rgb, sub_nir, sub_gt, sub_pan


# In[101]:


def pansharpening(sub_rgb, sub_pan):

    # RGB to HSV transformation
    array_hsv = rgb2hsv(sub_rgb)
    
    # Replacing "value" with pan subset
    array_hsv[:, :, 2] = sub_pan
    
    # Converting back to RGB
    pansharpend_rgb = hsv2rgb(array_hsv)
    
    return pansharpend_rgb

pansharpend_rgb = pansharpening(sub_rgb, sub_pan)


# In[118]:


aus_desert = pd.read_csv("Australian_Desert_Scenes.csv", index_col='Unnamed: 0')

row = ['103073', '103074', '104073']

path = "./data"

# Dimensions of Wanted Images
x = 384
y = 384

n = 2000  # Number of Sample images wanting to create

for i in range(n):
    
    folder = random.choice(row)
    
    ID = aus_desert.loc[folder].productId
    
    try:
        array_b, array_g, array_r, array_nir, array_qa, array_gt = read_files(path, folder, ID)
        print(ID+": Done read_files")
    
        sub_b, sub_g, sub_r, sub_nir, sub_gt, x1, x2, y1, y2 = qa_check_sub(x, y, array_b, array_g, array_r, array_nir, array_qa, array_gt)
        print(ID+": Done qa_check_sub")
    
        #sub_rgb, sub_nir, sub_gt, sub_pan = transform_subs(sub_b, sub_g, sub_r, sub_nir, sub_gt, sub_pan)
        #print(ID+": Done transform_subs")
    
        #pansharpend_rgb = pansharpening(sub_rgb, sub_pan)
        #print(ID+": Done pansharpening")
        
        batch_num = str(x1)+"_"+str(x2)+"_"+str(y1)+"_"+str(y2)
    
        patch_r = sub_r #pansharpend_rgb[:,:,0]
        file_name_r = "red_patch_" + ID + "_" + batch_num + ".tif"
        path_red = "./data/training_data/train_red/"+file_name_r
        imsave(fname=path_red, arr=patch_r)
        print(file_name_r +"  created")
    
        patch_g = sub_g #pansharpend_rgb[:,:,1]
        file_name_g = "green_patch_" + ID + "_" + batch_num + ".tif"
        path_green = "./data/training_data/train_green/"+file_name_g
        imsave(fname=path_green, arr=patch_g)
        print(file_name_g +"  created")

        patch_b = sub_b #pansharpend_rgb[:,:,2]
        file_name_b = "blue_patch_" + ID + "_" + batch_num + ".tif"
        path_blue = "./data/training_data/train_blue/"+file_name_b
        imsave(fname=path_blue, arr=patch_b)
        print(file_name_b +"  created")
    
        patch_nir = sub_nir
        file_name_nir = "nir_patch_" + ID + "_" + batch_num + ".tif"
        path_nir = "./data/training_data/train_nir/"+file_name_nir
        imsave(fname=path_nir, arr=patch_nir)
        print(file_name_nir +"  created")
    
        patch_gt = sub_gt
        file_name_gt = "gt_patch_" + ID + "_" + batch_num + ".tif"
        path_gt = "./data/training_data/train_gt/"+file_name_gt
        imsave(fname=path_gt, arr=patch_gt)
        print(file_name_gt +"  created")

    except ValueError:
        print("Value Error Made")
        continue
    except IndexError:
        print("Index Error Made")


# In[ ]:




