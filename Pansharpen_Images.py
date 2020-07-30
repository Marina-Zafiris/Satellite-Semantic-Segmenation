# needed to open GeoTIFF files
from osgeo import gdal
from gdalconst import *
import matplotlib.pyplot as plt
import numpy as np

# resize raster, and do HSV to RGB transformations
from skimage.transform import resize
from skimage.color import rgb2hsv, hsv2rgb

# define the file names for RGB and panchromatic (pan) images
# iterate or randomize through ID numbers in future
file_rgb = "./data/outputs/RGB_LC08_L1TP_109076_20170521_20170526_01_T1.tif"
file_pan = "./data/LC08_L1TP_109076_20170521_20170526_01_T1/LC08_L1TP_109076_20170521_20170526_01_T1_B8.TIF"

# load the data
try:
    data_rgb = gdal.Open(file_rgb, GA_ReadOnly)
    data_pan = gdal.Open(file_pan, GA_ReadOnly) 
except:
    print('error loading files')
    
# Initialize empty RGB array
columns = dataset_rgb.RasterXSize
rows = dataset_rgb.RasterYSize
rgb = np.zeros((rows, columns, 3))

# Fill array from TIFs
rgb[:,:,0] = data_rgb.GetRasterBand(3).ReadAsArray().astype(float)
rgb[:,:,1] = data_rgb.GetRasterBand(2).ReadAsArray().astype(float)
rgb[:,:,2] = data_rgb.GetRasterBand(1).ReadAsArray().astype(float)
pan = data_pan.GetRasterBand(1).ReadAsArray().astype(float)

# max pixel to normalize values
max_pix = 26032.0 #np.max(array_rgb)

# normalize RGB and pan
array_rgb = rgb / max_pix
array_pan = pan / max_pix

# must resize in order to replace value later
columns = data_pan.RasterXSize
rows = data_pan.RasterYSize
array_rgb = resize(array_rgb, (rows, columns))

# Checking the resize and normalization
print(np.shape(array_rgb))
print(np.shape(array_pan))
print(np.max(array_rgb))
print(np.max(array_pan))

#Making subset
#When we need random subset can be rand.int in interval
sub_array_rgb = array_rgb[9500:10000, 9500:10000, :]
sub_array_pan = array_pan[9500:10000, 9500:10000]

# HSV to RGB transform
array_hsv = rgb2hsv(sub_array_rgb)
# replacing value with pan
array_hsv[:, :, 2] = sub_array_pan
# converting back to RGB
NEW_array_rgb = hsv2rgb(array_hsv)

# Plotting for validation
output_fig, (pan_ax, value_ax) = plt.subplots(figsize=(12, 6), ncols=2)

pan_ax.imshow(sub_array_rgb)
pan_ax.set_title("Original Color image")

value_ax.imshow(NEW_array_rgb)
value_ax.set_title("Pan-Sharpened image")

plt.tight_layout()
#output_fig.savefig("OGvsPAN.png", format='png', dpi=200)