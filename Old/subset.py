#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Takes in the array dimmensions from qa_check and either directtly subsets or passes to pansharpening

def subset(bounds, bands):
    
    r1, r2, c1, c2 = bounds[0], bounds[1], bounds[2], bounds[3] 
    sub_bands = bands[r1:r2, c1:c2, :]
    
    # Make the option to pansharpen
    # Array bounds r1, r2, c1, c2 transformed to meet Pan Subset
    #pan_bounds = bounds*2
    #x1, x2, y1, y2 = pan_bounds[0], pan_bounds[1], pan_bounds[2], pan_bounds[3] 
    
    # Subsetting Pan
    #sub_pan = array_pan[x1:x2, y1:y2]
    
    return sub_bands