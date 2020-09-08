#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Main file

from read_file import read_files
from qa_check import qa_check
from subset import subset
from skimage.io import imsave

n = 2000 

path = './test'

folder = '103074'

ID = 'LC08_L1TP_103074_20140908_20170419_01_T1'

r,c = 384,384

bands, array_qa = read_files(path, folder, ID)
bounds = qa_check(r, c, array_qa)
sub_bands = subset(bounds, bands)

batch_num = str(bounds[0])+'_'+str(bounds[1])+'_'+str(bounds[2])+'_'+str(bounds[3])

colors = ['blue', 'green', 'red', 'nir', 'gt']

for i in range(len(colors)): 
    file_name = colors[i] + '_patch_' + ID + '_' + batch_num + '.tif'
    path = './training_data/train_' + colors[i] + '/' + file_name
    imsave(fname=path, arr=sub_bands[:,:,i])
    print(file_name +"  created")