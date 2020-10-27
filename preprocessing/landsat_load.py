# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.5.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

import sys
import datacube
import pandas as pd
from odc.ui import DcViewer
import numpy as np
# pip install rioxarray
import rioxarray
import xarray
import time


def landsat_load(rand_scene):
    
    # Uses the Longitute and Latitude and aquisition information from the selected random scene to load product in datacube
    x1 = float(rand_scene.min_lon)
    x2 = float(rand_scene.max_lon)
    y1 = float(rand_scene.min_lat)
    y2 = float(rand_scene.max_lat)
    date = str(rand_scene.acquisitionDate)[6:31]
    
    # Load data cube in python file name
    dc = datacube.Datacube(app="Landsat_Load")
    # Loads scene bands using above info
    ds = dc.load(product="ga_ls8c_ard_3",
             output_crs = "EPSG:32653",
             resolution = (-30, 30),
             x=(x1, x2),
             y=(y1, y2),
             measurements=["red", "green", "blue", "nir", "fmask"],
             time=date)
    
    # Save the xrarrays as np arrays at that single timestep (aquisition time)
    array_r = np.array(ds.red.isel(time=0))
    array_g = np.array(ds.green.isel(time=0))
    array_b = np.array(ds.blue.isel(time=0))
    array_nir = np.array(ds.nir.isel(time=0))
    array_fmask = np.array(ds.fmask.isel(time=0))
    
    # Stack the arrays along z axis
    bands = np.stack((array_b, array_g, array_r, array_nir), axis=2)
    
    # Saving one of the bands as a temporary tif for its parameters to be used to generate binary mask in raster_to_binary
    ds.red.rio.to_raster('../Aug2014Fires/test.tif')
    # Allows the tif to be generated before moving to next fuction?
    time.sleep(5)

    return bands, array_fmask


