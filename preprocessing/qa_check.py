#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np


def fmask_check(r, c, array_fmask):
    
    # Pixel value 1 in fmasks are clear terrain
    values_approved = [1]
    # Initialize the list with len = 1
    l = [0]
    
    while len(l) > 0:
        # Random lower bound
        r1 = np.random.randint(0, high=array_fmask.shape[0]-r, size=None, dtype='l') 
        # Upper bound with r distance from lower bound
        r2 = r1+r 
        # Random left bound
        c1 = np.random.randint(0, high=array_fmask.shape[1]-c, size=None, dtype='l') 
        # Right bounds with c distance from left bound
        c2 = c1+c    
        # Subset the Fmask
        sub_array_fmask = array_fmask[r1:r2, c1:c2]    
        # Check pixel values within subset
        values_qa = list(np.sort(np.unique(sub_array_fmask)))
        # Creates a list of pixel values that are not approved, will pass once list is empty, aka all the pixel values in the subset are 1
        l = list(filter(lambda num: (num not in values_approved), values_qa))     
        
    bounds = [r1, r2, c1, c2]

    return bounds


