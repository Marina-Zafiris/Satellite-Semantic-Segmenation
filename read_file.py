#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Read in TIF Files as arrays
# Currently reads R, G, B, NIR, and GT. Will be incorporating pan band as well
# Stacks all arrays along z-axis


import numpy as np
from PIL import Image

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
    
    file_gt = path + "/" + folder + "/" + ID + "_GT.tif" #Ground Truth 
    tif_gt = Image.open(file_gt)
    array_gt = np.array(tif_gt, dtype = int)
    
    # fills array gt, dimmensions are slightly off
    # MS shapes are (7795, 7602)
    # GT shapes are (7717, 7600)
    # potentially removable if GT can be made with sam dim in QGIS
    rows = array_b.shape[0]-array_gt.shape[0]
    row_fill = np.zeros((rows, array_gt.shape[1]), dtype=int)
    array_gt = np.append(array_gt, row_fill , axis=0)
    cols = array_b.shape[1]-array_gt.shape[1]
    cols_fill = np.zeros((array_gt.shape[0], cols), dtype=int)
    array_gt = np.append(array_gt, cols_fill , axis=1)
    
    bands = np.stack((array_b, array_g, array_r, array_nir, array_gt), axis=2)
    
    return bands, array_qa
