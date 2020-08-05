import os
#from osgeo import gdal
from PIL import Image
import PIL
import numpy as np
PIL.Image.MAX_IMAGE_PIXELS = 933120000
import exifread

# Input/Output
def get_img_dir(key):
  # Ultimately, this should return the image directory for the input key within
  # a larger geodatabase. For now, it just returns the directory for one
  # prototype image, and otherwise throws an error

  if key == '110076_20170816_20170825_01':
    d = os.path.expanduser('~') 
    d = os.path.join(d,'Downloads/LC08_L1TP_110076_20170816_20170825_01_T1')
    return(d)
  else:
    raise Exception('key = ',key,'not in database')

def get_img_path(key,which='pan'):
  d = get_img_dir(key)

  f = os.path.join(d,'LC08_L1TP_' + key + '_T1_B')
  if (which == 'pan') or (which == '8'):
    f = f + '8'
  elif (which == 'qa'):
    f = f + 'QA'
  elif (which == 'red'):
    f = f + '4'
  else:
    raise Exception('which = ' + which + ' option not recognized')
  f = f + '.TIF'
  return(f)

def get_img(key,which='pan'):
  f = get_img_path(key,which)
  return(np.asarray(Image.open(f)))

def get_random_subset_ind(key,Nu,Nv):
  # This could be done more efficiently (e.g., by not reading in the entire
  # file).
  qa = get_img(key,'qa')
  nu0 = np.random.randint(0, qa.shape[0]-Nu, size=None, dtype='l')
  nv0 = np.random.randint(0, qa.shape[1]-Nv, size=None, dtype='l')
  qa = qa[slice(nu0,nu0+Nu),slice(nv0,nv0+Nv)]

  # Acceptable pixels are 2738 and 2720
  # Do this more efficiently in the future (for loops are easy to code and
  # understand, but slow). At least it terminates early once a "bad" pixel is
  # found
  for nu in range(0,qa.shape[0]):
    for nv in range(0,qa.shape[1]):
      if not (qa[nu,nv] in [2720,2738]):
        return None
  
  return([nu0,nv0,Nu,Nv])

def get_spatial_info(key,which='pan'):
  fileName = get_img_path(key,which)
  f = open(fileName,'rb')
  tags = exifread.process_file(f)
  resInfo = tags['Image Tag 0x830E'].values
  offsetInfo = tags['Image Tag 0x8482']
  refFrameInfo = tags['Image Tag 0x87B1']
  return((resInfo,offsetInfo,refFrameInfo))
