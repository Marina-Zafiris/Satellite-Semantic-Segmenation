# Import necessary packages
import sys
import datacube
import pandas as pd
import numpy as np
import geopandas as gpd
from odc.ui import DcViewer
import shapefile

from shapely.geometry import mapping
import rioxarray as rxr
import xarray as xr
import geopandas as gpd
import shapefile
import sys
import datacube

# Loading Datacube
dc = datacube.Datacube(app="main")




def clip_filter(shapes, i, train_df):
    """
    - takes geometry extent and loads R,G,B,NIR, FMASK for give start and end times
    - iterates over the timestep range
    - clips raster arrrays to polygon borders
    - fmask check to ensure values within the border are clear
    - if it passes fmask it will take the R,G,B,NIR layers and place them into 1D array
    - if it fails it will skips that timestep and pass to next one
    - organizes above into nested lists
    
    """
    
    # from shape file polygon, load polygon extent
    x1 = shapes[i].bbox[0]
    x2 = shapes[i].bbox[2]
    y1 = shapes[i].bbox[1]
    y2 = shapes[i].bbox[3]
    
    # time frame of interest
    date1 = '2014-01-01'
    date2 = '2014-08-28'
    
    # landsat raster stack
    ds1 = dc.load(product="ga_ls8c_ard_3",
                  output_crs = "EPSG:32653",
                  resolution = (-30, 30),
                  x=(x1, x2),
                  y=(y1, y2),
                  crs = "EPSG:3112",
                  measurements=["red", "green", "blue", "nir", "fmask"],
                  time=(date1, date2))
   
    all_values= []
    
    # iterate through timesteps
    for t in range(len(ds1.time)):
        timestep = ds1.isel(time=t)
        # clip rasters of timestep according to polgon
        clipped = timestep.rio.clip(train_df.geometry.apply(mapping), train_df.crs, drop=False, invert=False)
        
        #flags_definition :
        #    {'fmask': {'bits': [0, 1, 2, 3, 4, 5, 6, 7], 
        #    'values': {'0': 'nodata', '1': 'valid', '2': 'cloud', '3': 'shadow', '4': 'snow', '5': 'water'}
        fmask_values = list(np.unique(clipped.fmask))
        pass_values = list(np.array([0, 1]))
        
        if fmask_values == pass_values:
            # Passed fmask check
            # creates standard np.array with R, G, B, NIR
            clip_copy = np.array(clipped.to_array())[0:4, :, :]
            # takes all the valid datapoints and places them in list
            time_stamp = str(np.array(ds1.time[t]))[0:10]
            value_list = [time_stamp]
            
            for value in np.nditer(clip_copy):
                if value != -999:
                    value_list.append(int(value))
            
            all_values.append(value_list)
        else:
            pass
                
    return all_values



# citation: https://gist.github.com/GaelVaroquaux/ead9898bd3c973c40429

def mutual_information_2d(x, y, sigma=1, normalized=False):
    """
    Computes (normalized) mutual information between two 1D variate from a
    joint histogram.
    Parameters
    ----------
    x : 1D array
        first variable
    y : 1D array
        second variable
    sigma: float
        sigma for Gaussian smoothing of the joint histogram
    Returns
    -------
    nmi: float
        the computed similariy measure
    """
    bins = (256, 256)



    jh = np.histogram2d(x, y, bins=bins)[0]

    # smooth the jh with a gaussian filter of given sigma
    ndimage.gaussian_filter(jh, sigma=sigma, mode='constant',
                                 output=jh)

    # compute marginal histograms
    jh = jh + EPS
    sh = np.sum(jh)
    jh = jh / sh
    s1 = np.sum(jh, axis=0).reshape((-1, jh.shape[0]))
    s2 = np.sum(jh, axis=1).reshape((jh.shape[1], -1))

    # Normalised Mutual Information of:
    # Studholme,  jhill & jhawkes (1998).
    # "A normalized entropy measure of 3-D medical image alignment".
    # in Proc. Medical Imaging 1998, vol. 3338, San Diego, CA, pp. 132-143.
    if normalized:
        mi = ((np.sum(s1 * np.log(s1)) + np.sum(s2 * np.log(s2)))
                / np.sum(jh * np.log(jh))) - 1
    else:
        mi = ( np.sum(jh * np.log(jh)) - np.sum(s1 * np.log(s1))
               - np.sum(s2 * np.log(s2)))

    return mi


def main():
    """
    - iterates through the 2014WDFiresAllEPSG3112.shp geometries
    - calls clip_filter and mutual_information_2d
    - MI value is stored into dictionary
    """
    # Reading in shape file for extext bound
    shape_path = '../Aug2014Fires/2014WDFiresAllEPSG3112.shp'
    sf = shapefile.Reader(shape_path)
    shapes = sf.shapes()
    
    # FOR TEST PURPOSES
    # shapes = shapes[0:5]
    
    # also reading using geopandas for geometry feature benefits
    train_df = gpd.read_file(shape_path)
    train_df = train_df.to_crs("EPSG:32653")
    
    # For MI
    EPS = np.finfo(float).eps
    
    shapes_mi_dict = {}
    
    for i in range(len(shapes)):
        all_values = clip_filter(shapes, i, train_df)
        
        mi_dict = dict()
        
        for j in range(len(all_values)-1):
            x = np.array(all_values[j][1:])
            y = np.array(all_values[j+1][1:])
            
            mi = mutual_information_2d(x, y, sigma=1, normalized=False)
            
            date_range = str(all_values[j][0]+ " to "+ all_values[j+1][0])
            
            mi_dict[date_range] = mi
        
        shapes_mi_dict[i] = mi_dict
        
    return shapes_mi_dict