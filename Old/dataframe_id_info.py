#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  8 13:53:03 2020

@author: marinazafiris
"""

import pandas as pd
#102_69

s3_scenes = pd.read_csv('http://landsat-pds.s3.amazonaws.com/c1/L8/scene_list.gz', compression='gzip')

aus_desert = s3_scenes[(s3_scenes['path'] == 107) & (s3_scenes['row'] == 76)]