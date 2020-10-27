#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import datacube
import pandas as pd
from odc.ui import DcViewer

dc = datacube.Datacube(app="Landsat_Load")

Landsat_Scenes = pd.read_csv("Scripts/Australian_Desert_Scenes.csv")

rand_scene = Landsat_Scenes.sample()
x1 = float(rand_scene.min_lon)
x2 = float(rand_scene.max_lon)
y1 = float(rand_scene.min_lat)
y2 = float(rand_scene.max_lat)
date = str(rand_scene.acquisitionDate)[6:31]

ds = dc.load(product="ga_ls8c_ard_3",
             output_crs = "EPSG:32653",
             resolution = (-30, 30),
             x=(x1, x2),
             y=(y1, y2),
             measurements=["red", "green", "blue", "nir", "fmask"],
             time=date)

