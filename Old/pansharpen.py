#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
# resize raster, and do HSV to RGB transformations
from skimage.transform import resize
from skimage.color import rgb2hsv, hsv2rgb


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


def pansharpening(sub_rgb, sub_pan):

    # RGB to HSV transformation
    array_hsv = rgb2hsv(sub_rgb)
    
    # Replacing "value" with pan subset
    array_hsv[:, :, 2] = sub_pan
    
    # Converting back to RGB
    pansharpend_rgb = hsv2rgb(array_hsv)
    
    return pansharpend_rgb

pansharpend_rgb = pansharpening(sub_rgb, sub_pan)