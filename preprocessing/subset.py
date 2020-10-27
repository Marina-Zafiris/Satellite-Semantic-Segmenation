#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np 


def subset_bands(bounds, bands, mask):
    
    r1, r2, c1, c2 = bounds[0], bounds[1], bounds[2], bounds[3] 
    # Subseting the G,B,R,NIR and the GT based on the x,y bounds
    sub_gbrnir = bands[r1:r2, c1:c2, :]
    sub_gt = mask[r1:r2, c1:c2]
    # Stacking the bands to be easily saved in main script
    sub_bands = np.dstack((sub_gbrnir, sub_gt))
    
    return sub_bands


