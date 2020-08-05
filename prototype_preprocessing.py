import semseg as seg
from PIL import Image
import PIL
import numpy as np

PIL.Image.MAX_IMAGE_PIXELS = 933120000

key = '110076_20170816_20170825_01'

#img_dir = seg.get_img_dir(key)

#pan = seg.get_img(key)
#qa  = seg.get_img(key,which='qa')
#red = seg.get_img(key,which='red')
#print(pan.shape)
#print(red.shape)
#print(qa.shape)

# Draw 100 random subset indices

#for n in range(0,100):
#  print(seg.get_random_subset_ind(key,75,50))

print(seg.get_spatial_info(key,'pan'))
print(seg.get_spatial_info(key,'qa'))
print(seg.get_spatial_info(key,'red'))
