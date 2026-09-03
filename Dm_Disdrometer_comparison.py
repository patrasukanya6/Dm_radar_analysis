"""Create a temperature-matched disdrometer Dm dataset for one day.

The script is invoked with four positional command-line arguments::

    python Dm_Disdrometer_comparison.py SCRIPT_NAME DATE OUTPUT_DIR DISDROMETER_DIR

``DATE`` identifies the processing day.  The workflow downloads the daily
Cloudnet ECMWF model file, calculates mass-weighted mean diameter (Dm) from
Parsivel disdrometer measurements, removes invalid values and non-rain cases,
and matches each disdrometer timestamp with the nearest model temperature at
the MIM station height (approximately 538 m AMSL).

The resulting Dm and temperature time series are written to
``OUTPUT_DIR/YYYYMMDD_Dm_disdrometer_comparison_Temp.nc``.  The script runs at
import time because it reads its command-line arguments immediately.
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

import requests
from Dm_Calculation_for_disdrometer import Dm_Cal

scriptname, date, pathOutputData, pathDisdrometer = argv

import logging

# Output log file
logfile = '/home/m/met-actris/scripts/actris/quicklooks/Resample_Data/Dm_disdrometer_for_sat_comparison.log'

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
logger.info('temperature data from ERA5 download start')



date = pd.to_datetime(date)
year=date.strftime('%Y')
month=date.strftime('%m')
day=date.strftime('%d')
date1=date.strftime('%Y-%m-%d')

try:
    # Download the model file from Cloudnet, which provides the ECMWF data
    # used for the temperature match below.
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

    fileNameTemp = date.strftime('%Y%m%d')+'_munich_ecmwf.nc'
    fntemp= ('/').join([pathOutputData, fileNameTemp])
    dataset_temp=xr.open_dataset(fntemp)#,chunks={'time':5000})
    temperature1=dataset_temp.temperature

    ####------------------------------classifying Disdrometer data according to the surface temperature --------------------------------------

    fn_disdro=pathDisdrometer+date.strftime('%Y')+'/'+date.strftime('%m')+'/'+date.strftime('%Y')+date.strftime('%m')+date.strftime('%d')+'_parsivel2.nc'
    dataset_disdro=xr.open_dataset(fn_disdro)
    Dm_parsivel= Dm_Cal(date, pathDisdrometer)
    # Exclude invalid Dm values, solid precipitation, and measurements made
    # while the disdrometer housing was at or below 3 degrees C.
    Dm_parsivel[Dm_parsivel<0]=np.nan

    Dm_parsivel[np.where(dataset_disdro['wawa']>61)]=np.nan  ## to extract the cases for snow and haili
    Dm_parsivel[np.where(dataset_disdro['T_sensor_housing']<=3)]=np.nan
    Dm_parsivel=xr.DataArray(Dm_parsivel)
    Dm_parsivel=Dm_parsivel.assign_coords(dim_0=dataset_disdro.time.values)
    Dm_parsivel=Dm_parsivel.rename({'dim_0':'time'})

    # Extract one model level near the MIM station elevation (490-560 m AMSL)
    # for each model timestamp, then align it to disdrometer timestamps.
    temp_dis=[]
    for i in range(0, dataset_temp.height.shape[0]):temp_dis.append(temperature1[i,np.where(np.logical_and(dataset_temp.height[i, :].values > 490, dataset_temp.height[i, :].values < 560))[0][0]].values)
    temp_dis=xr.DataArray(temp_dis)
    temp_dis=temp_dis.assign_coords(dim_0=dataset_temp.time.values)
    temp_dis=temp_dis.rename({'dim_0':'time'})
    temperature_dis=temp_dis.reindex({'time':dataset_disdro.time},method='nearest')
    
    
    df= xr.Dataset({})
    df['Dm_Parsivel']=Dm_parsivel
    df['temperature']=temperature_dis
    df.Dm_Parsivel.attrs['units']='mm'
    df.Dm_Parsivel.attrs['long_name']='mean mass weighted diameter in mm'
    
    outPutFileName=pathOutputData+date.strftime('%Y%m%d')+'_Dm_disdrometer_comparison_Temp.nc'
    if os.path.exists(outPutFileName):os.remove(outPutFileName)
    df.to_netcdf(pathOutputData+date.strftime('%Y%m%d')+'_Dm_disdrometer_comparison_Temp.nc')
    print(pathOutputData+date.strftime('%Y%m%d')+'_Dm_disdrometer_comparison_Temp.nc')


except TypeError:
    logger.info('no Dm_radar data on '+date.strftime('%Y%m%d'))
