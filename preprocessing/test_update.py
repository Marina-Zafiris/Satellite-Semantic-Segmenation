#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Import necessary functions from other scripts
import sys
#sys.path.append('./')
from landsat_load import landsat_load
from raster_to_binary import binary_mask
from qa_check import fmask_check
from subset import subset_bands

# Other Needed Packages
import numpy as np
import pandas as pd
import time
from skimage.io import imsave

# +
# Wanted number of training subsets 

# Dataframe contains all the respective scenes of interest
Landsat_Scenes = pd.read_csv("../Aug2014Fires/Australian_Desert_Scenes.csv")

# desired subset dimensions, rows (r) columns (c)
r,c = 384,384
n = 20
n_sub = 20

def main(n, n_sub, r, c):
    for i in range(n):
        # Randomly select a scene to subset
        rand_scene = Landsat_Scenes.sample()
        # Loads the rand_scene through datacube and makes into stacked R,G,B,NIR array
        bands, array_fmask = landsat_load(rand_scene)
        print("done landsat load " + str(i))
        
        # Creates binary mask (ground truth) for the given scene
        mask = binary_mask()
        print("done mask")
        
            #Creates 20 subsets from that random scene selection
        for i in range(n_sub):

            # Generated the bounds for the subseting by passing fmask clearence check
            bounds = fmask_check(r, c, array_fmask)
            print("done check")

            # Given the bounds above, Subsets the R,G,B,NIR & Binary arrays
            sub_bands = subset_bands(bounds, bands, mask)
            print("done subset")

            # Creates unique ID name for the subset
            ID = str(rand_scene.entityId)[6:27]
            batch_num = str(bounds[0])+'_'+str(bounds[1])+'_'+str(bounds[2])+'_'+str(bounds[3])

            # Saving the arrays as TIFs in respective directories
            colors = ['blue', 'green', 'red', 'nir', 'gt']
            for i in range(len(colors)):
                file_name = colors[i] + '_patch_' + ID + '_' + batch_num + '.tif'
                path = '../training_data/train_' + colors[i] + '/' + file_name
                imsave(fname=path, arr=sub_bands[:,:,i])
                print(file_name +"  created")


# -
main(n, n_sub, r, c)
