"""Create temperature-filtered radar Dm comparison data for one day.

The script is invoked with five positional command-line arguments::

    python Dm_radar_comparison_final.py SCRIPT_NAME DATE OUTPUT_DIR 
        Dm_radar_TEMP_FILTER_DIR PLOT_DIR

``DATE`` is parsed by pandas and identifies the day to process.  The workflow
retrieves radar mass-weighted mean equivolume diameter (Dm), removes insect
classified pixels, downloads the day's Cloudnet ECMWF temperature file, and
keeps radar values warmer than 276 K.  The filtered values and matching
temperatures are flattened and written to a daily NetCDF file.  A quicklook
plot is written when at least one valid Dm value remains.

OUTPUT_DIR is the directory where the radar Dm and Cloudnet classification files are
expected to be found.  

Dm_radar_TEMP_FILTER_DIR is the directory where the flattened
NetCDF file is written.  

PLOT_DIR is the directory where the quicklook plot is saved.

This module intentionally remains a script: all processing occurs at import
time because the command-line arguments are consumed immediately.
"""

from scipy.interpolate import interp1d
from itertools import count
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import glob
from netCDF4 import Dataset
from pylab import get_current_fig_manager
import time as time_app
from datetime import date
import xarray as xr
import os
import math
from matplotlib.ticker import MultipleLocator
import shutil
import geopy.distance
from math import sin, cos, sqrt, atan2, radians
from datetime import datetime, timedelta
from sys import argv
import os
from Dm_radar_estimation_function import Dm_radar_estimation
import requests
scriptname,date, pathOutputData ,pathDmData_tempfilter , DiffRadarPlots = argv

import logging



os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"
os.environ["OPENBLAS_NUM_THREADS"] = "2"
# Output log file
logfile = '/home/m/met-actris/scripts/actris/quicklooks/Resample_Data/Dm_radar_for_sat_comparison.log'

# Create logger instance
logger = logging.getLogger(__name__)

# Define logger format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Set output file handler
file_handler = logging.FileHandler(logfile)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Set output stream handler
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)

date = pd.to_datetime(date)
year=date.strftime('%Y')
month=date.strftime('%m')
day=date.strftime('%d')
date1=date.strftime('%Y-%m-%d')


try:
    # Radar retrieval returns Dm on the radar time/range grid.
    logger.info('Dm retrieval from DDV starts')

    ####-------------------------------extracting the ground based radar Dm from the nc file-------------------
    dataset=Dm_radar_estimation(date,pathOutputData)
    Dm_radar=dataset['Dm_radar']
    Dm_radar=Dm_radar.where(Dm_radar>=0)
    logger.info('Dm retrieval from DDV ends')

    # Reindex Cloudnet classification to the radar reference grid before
    # removing insect-only and insect/aerosol classification values.
    
    logger.info('biota filtering starts')

    fileNameClass = date.strftime('%Y%m%d')+'_munich_classification.nc'
    fnclass= ('/').join([pathOutputData, fileNameClass])
    dataset_class=xr.open_dataset(fnclass,chunks={'time':5000})
#Z94.where(dataset['target_classification']==3)
    beginRangeRef = 538 # starting height of the ref grid ##adding 538 meter (MIM station height AMSL) to convert from AGL to AMSL, since CLoudNet data is already in AMSL
    endRangeRef = 12000+538 # ending height of the ref grid
    rangeFreq = 36 # range resolution of the ref grid
    rangeTolerance = 18 # tolerance for detecting the closest neighbour
    rangeRef = np.arange(beginRangeRef, endRangeRef, rangeFreq)

    timeTolerance = '2S'
    timeFreq = '4S'
# getting the time reference grid
    timeRef = pd.date_range(date, date+pd.offsets.Day(1)-pd.offsets.Second(1), freq=timeFreq)

    dataset_class=dataset_class.reindex({'height':rangeRef},method='nearest')#,tolerance=rangeTolerance)
    dataset_class=dataset_class.reindex({'time':timeRef},method='nearest')#,tolerance=timeTolerance)
    dataset_class=dataset_class.rename({'height':'range'})
    
    Dm_radar=Dm_radar.where(dataset_class['target_classification'].values<8) ####Dataset_class['target_classification'].definition 9: Insects, no cloud or precipitation.\nValue 10: Aerosol coexisting with insects, no cloud or precipitation.'
    logger.info('biota filtering ends')
    print(len(np.where(~np.isnan(Dm_radar[:,:112]))[0]))
    if (len(np.where(~np.isnan(Dm_radar[:,:112]))[0]) > (7884*112*20)/100 ):# condition of 50% of Dm_radar data should not be nan;for removing cases with small rain duratio#n; i did not take full range(334), I took upto 4000 m which comes at Dm_radar.range[112] because thats the maximum height for rain
## though the total no of profils are 21600 (24*15*60), since zenith scan is not continuous, it is for 1314 sec in one hour (219 sce * 6 scans per hour), and hence in a day #total zenith scan duration is 31536 (1314*24), and radar resolution is 4 sec, so the no of profiles would be 7884 (31536/4) i.e the Maximum no of points in a day in one r#ange bin assuming there is cloud throughout the zen scan,hence the total no of maximum data points considering all the range bins upto 4 km is 112*7884

    # Cloudnet provides the ECMWF/ERA-5 temperature file more quickly
    # than querying the upstream ERA-5 service directly.
        logger.info('temperature data from CloudNet  download starts')

        url = 'https://cloudnet.fmi.fi/api/model-files'
        payload = {
            'date': date1,       # e.g., '2024-10-21'
            'site': 'munich',    # site ID for Munich
            'model': 'ecmwf'     # Optional: specify the model to avoid empty results if multiple exist
        }
        response = requests.get(url, params=payload)
        metadata = response.json()
        for row in metadata:res = requests.get(row['downloadUrl'])
        with open(pathOutputData+row['filename'], 'wb') as f:
            f.write(res.content)

        logger.info('temperature data interpolation starts')

        fileNameTemp = date.strftime('%Y%m%d')+'_munich_ecmwf.nc'
        fntemp= ('/').join([pathOutputData, fileNameTemp])
        dataset_temp=xr.open_dataset(fntemp,chunks={'time':5000})
        temperature=dataset_temp.temperature
        time=np.repeat(dataset_temp.time.values[np.newaxis, :], dataset_temp.height.shape[0] ,axis=0) #137, axis=0)
        
        #plt.figure(figsize=(12, 4))
        #plt.pcolor(time.T,dataset_temp.height/1000,temperature,cmap='turbo')
        #plt.colorbar()
        #plt.contour(time.T,dataset_temp.height/1000,temperature.where(temperature.values>276), levels=10, colors='black')
        #plt.ylim(0,12)
        #plt.grid(True, linestyle='--')
        #plt.ylabel('Height (km) AMSL')
        #plt.xlabel('Time')
        #my_file = f'Temperature_276_BI'+date.strftime('%Y%m%d')+'.png'
        #plt.savefig(os.path.join(DiffRadarPlots, my_file), bbox_inches='tight', dpi=500)
        #print(os.path.join(DiffRadarPlots, my_file))

        temperature = temperature.assign_coords(level=dataset_temp.height[1, :].values).rename({"level": "height"})
        beginRangeRef = 538 # starting height of the ref grid
        endRangeRef = 12000+538 # ending height of the ref grid
        rangeFreq = 36 # range resolution of the ref grid
        rangeTolerance = 18 # tolerance for detecting the closest neighbour
        rangeRef = np.arange(beginRangeRef, endRangeRef, rangeFreq)
        timeTolerance = '2S'
        timeFreq = '4S'
        timeRef = pd.date_range(date, date+pd.offsets.Day(1)-pd.offsets.Second(1), freq=timeFreq)

        temperature=temperature.reindex({'height':rangeRef},method='nearest')#,tolerance=rangeTolerance)
        temperature=temperature.reindex({'time':timeRef},method='nearest')#,tolerance=timeTolerance)
        
        
        #plt.figure(figsize=(12, 4))
        #plt.pcolor(timeRef,rangeRef/1000,temperature.T,cmap='turbo')
        #plt.colorbar()
        #plt.contour(timeRef,rangeRef/1000,temperature.where(temperature.values>276).T, levels=10, colors='black')
        #plt.ylim(0,12)
        #plt.grid(True, linestyle='--')
        #plt.ylabel('Height (km) AMSL')
        #plt.xlabel('Time')
        #my_file = f'Temperature_276_AI'+date.strftime('%Y%m%d')+'.png'
        #plt.savefig(os.path.join(DiffRadarPlots, my_file), bbox_inches='tight', dpi=500)
        #print(os.path.join(DiffRadarPlots, my_file))


        # Rain Dm is retained only where the model temperature is above the
        # 276 K melting-layer threshold used by this processing chain.
        Dm_radar=Dm_radar.where(temperature.values>276)

        if (~np.isnan(np.nanmean(Dm_radar))):
            plt.figure(figsize=(10, 8))
            Dm_radar.T.plot(cmap='turbo',vmin=0,vmax=2)
            plt.ylim(0,4000)
            plt.grid(True, linestyle='--')
            my_file = f'Rain_Dm_radar_HTI_'+date.strftime('%Y%m%d')+'.png'
            plt.savefig(os.path.join(DiffRadarPlots, my_file), bbox_inches='tight', dpi=500)
            print(os.path.join(DiffRadarPlots, my_file))
        #print(len(np.where(~np.isnan(Dm_radar[:,:112]))[0]))

        #if (len(np.where(~np.isnan(Dm_radar[:,:56]))[0]) > (7884*56*20)/100):# condition of 50% of Dm_radar data should not be nan;for removing cases with small rain duratio#n; i did not take full range(334), I took upto 2000 m which comes at Dm_radar.range[56] because after temperature correction normally cloud goes upto 2 km
            # Drop entirely empty time and range bins before serialisation;        
            temperature=temperature[:,np.where(~np.isnan(np.nanmean(Dm_radar,axis=0)))[0]]
            Dm_radar=Dm_radar[:,np.where(~np.isnan(np.nanmean(Dm_radar,axis=0)))[0]]
            
            temperature=temperature[np.where(~np.isnan(np.nanmean(Dm_radar,axis=1)))[0],:]
            Dm_radar=Dm_radar[np.where(~np.isnan(np.nanmean(Dm_radar,axis=1)))[0],:]
            logger.info('Dm for rain using temperature ends')
            print(len(np.where(~np.isnan(Dm_radar[:,:56]))[0]))
           
            logger.info('saving the data')


            # flattening keeps Dm and temperature aligned element by element.
            df= xr.Dataset({})
            df['Dm_radar']=Dm_radar.values.flatten()
            df['temperature']=temperature.values.flatten()
            df.Dm_radar.attrs['units']='mm'
            df.Dm_radar.attrs['long_name']='mass weighted mean equivolume diameter in mm'
            
            outPutFileName=pathDmData_tempfilter+date.strftime('%Y%m%d')+'_Dm_radar_comparison_TempFilt.nc'
            if os.path.exists(outPutFileName):os.remove(outPutFileName)
            df.to_netcdf(outPutFileName)
            print(outPutFileName)
        else:
            logger.info('Not enough rain today')
    else:
        logger.info('Not enough data point today')

except TypeError:
    logger.info('no Dm_radar data on '+date.strftime('%Y%m%d'))
