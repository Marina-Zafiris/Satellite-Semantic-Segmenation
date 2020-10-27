#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Generate approved bounds by conducting QA check within randomly selected bound regions
# Approval for subsets that only contain pixel value of 2720

import numpy as np

def qa_check(r, c, array_qa):
    
    values_approved = [2720.0]
    l = [0]
    
    while len(l) > 0:
        r1 = np.random.randint(0, high=array_qa.shape[0]-r, size=None, dtype='l') # Random lower bound
        r2 = r1+r                                                                 # Upper bound with r distance from lower bound
        c1 = np.random.randint(0, high=array_qa.shape[1]-c, size=None, dtype='l') # Random left bound
        c2 = c1+c                                                                 # Right bounds with c distance from left bound
        sub_array_qa = array_qa[r1:r2, c1:c2]                                     # Subset the QA
        values_qa = list(np.sort(np.unique(sub_array_qa)))                        # Check pixel values within subset
        l = list(filter(lambda num: (num not in values_approved), values_qa))     # Creates a list of pixel values that are not approved
        
    bounds = [r1, r2, c1, c2]

    return bounds
