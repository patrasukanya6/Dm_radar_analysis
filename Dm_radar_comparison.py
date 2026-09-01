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
from Dm_quicklooks_earthcare import Dm_radar_for_earthcare
import cdsapi
import requests
scriptname,date,pathOutputData = argv

import logging

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
logger.info('temperature data from ERA5 download start')



date = pd.to_datetime(date)
year=date.strftime('%Y')
month=date.strftime('%m')
day=date.strftime('%d')
date1=date.strftime('%Y-%m-%d')


#################------------------downloading temperature data from ERA-5 site directly-----------------
#try:
#c = cdsapi.Client()
#c.retrieve(
#     'reanalysis-era5-pressure-levels',
#     {
#         'product_type': 'reanalysis',
#         'format': 'netcdf',
#         'variable': 'temperature',
#         'pressure_level': [
#             '250', '300', '350', '400', '450', '500',
#             '550', '600', '650', '700', '750', '775', '800', '825', '850', '875',
#             '900', '925', '950', '975', '1000'
#         ],
#         'year': year,
#         'month': month,
#         'day': day,
#          'time': [f'{h:02d}:00' for h in range(24)], # All 24 hours
#         'area': [48.3, 11.4, 48.1, 11.6], # Munich Bounding Box
#     },
#     pathOutputData+'munich_temperature_profile_'+date.strftime('%Y%m%d')+'.nc')

            

#except:logger.info('no era5 data on '+date.strftime('%Y%m%d'))


try:

    ####-------------------------------extracting the ground based radar Dm from the nc file-------------------
    dataset=Dm_radar_for_earthcare(date,pathOutputData)
    Dm_radar=dataset['Dm_radar']

###-------------------------insects filtering with the help og the CloudNet classification data------------
    fileNameClass = date.strftime('%Y%m%d')+'_munich_classification.nc'
    fnclass= ('/').join([pathOutputData, fileNameClass])
    dataset_class=xr.open_dataset(fnclass)#,chunks={'time':5000})
#Z94.where(dataset['target_classification']==3)
    beginRangeRef = 0 # starting height of the ref grid
    endRangeRef = 12000 # ending height of the ref grid
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
    
    Dm_radar=Dm_radar.where(dataset_class['target_classification']<8) ####Dataset_class['target_classification'].definition 9: Insects, no cloud or precipitation.\nValue 10: Aerosol coexisting with insects, no cloud or precipitation.'

######------------------Download ERA-5 model temperature data from cloudnet site (becauise it is FASTER than ERA-5 site)---------------------
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
    temperature=dataset_temp.temperature
    temperature = temperature.assign_coords(level=dataset_temp.height[1, :].values).rename({"level": "height"})
    beginRangeRef = 0 # starting height of the ref grid
    endRangeRef = 12000 # ending height of the ref grid
    rangeFreq = 36 # range resolution of the ref grid
    rangeTolerance = 18 # tolerance for detecting the closest neighbour
    rangeRef = np.arange(beginRangeRef, endRangeRef, rangeFreq)

    timeTolerance = '2S'
    timeFreq = '4S'
# getting the time reference grid
    timeRef = pd.date_range(date, date+pd.offsets.Day(1)-pd.offsets.Second(1), freq=timeFreq)

    temperature=temperature.reindex({'height':rangeRef},method='nearest')#,tolerance=rangeTolerance)
    temperature=temperature.reindex({'time':timeRef},method='nearest')#,tolerance=timeTolerance)
    temperature=temperature.rename({'height':'range'})
    
    Dm_radar['range']=Dm_radar.range+520 #converting AGL to AMSL
    Dm_radar=Dm_radar.where(temperature.values>276)

    #plt.figure(figsize=(10, 8))
    #Dm_radar.plot(cmap='turbo')
    #my_file = f'Rain_Dm_radar_HTI_'+date.strftime('%Y%m%d')+'.png'
    #plt.savefig(os.path.join(DiffRadarPlots, my_file), bbox_inches='tight', dpi=500)


    ####----------------interpolation of temperature data into radar data resoltuion--------------------

    beginRangeRef = 520 # starting height of the ref grid
    endRangeRef = 12000+520 # ending height of the ref grid
    rangeFreq = 36 # range resolution of the ref grid
    rangeTolerance = 18 # tolerance for detecting the closest neighbour
    rangeRef = np.arange(beginRangeRef, endRangeRef, rangeFreq)

    timeTolerance = '2S'
    timeFreq = '4S'
# getting the time reference grid
    timeRef = pd.date_range(date, date+pd.offsets.Day(1)-pd.offsets.Second(1), freq=timeFreq)
    fn_t=pathOutputData+'munich_temperature_profile_'+date.strftime('%Y%m%d')+'.nc'
    data_temp=xr.open_dataset(fn_t)
    ht_temp=44330 * (1 - (data_temp.pressure_level/ 1013.25)**0.1903)
    data_temp=data_temp.assign_coords(height=ht_temp)
    temperature=data_temp.t.squeeze( ['latitude','longitude'  ]  )
    temperature=temperature.swap_dims({"pressure_level": "height"})
    temperature=temperature.interp(coords={"height":rangeRef},method="linear")
    temperature=temperature.interp(coords={"valid_time":timeRef},method="linear",kwargs={"fill_value": "extrapolate"})
    

    Dm_radar['range']=Dm_radar.range+520 #converting AGL to AMSL
    #print(Dm_radar['range'].values)
    Dm_radar=Dm_radar.where(temperature.values>276)
    temperature=temperature[:,np.where(~np.isnan(np.nanmean(Dm_radar,axis=0)))[0]]
    Dm_radar=Dm_radar[:,np.where(~np.isnan(np.nanmean(Dm_radar,axis=0)))[0]]
    
    plt.figure(figsize=(10, 8))
    Dm_radar.plot(cmap='turbo')
    my_file = f'Rain_Dm_radar_HTI_'+date.strftime('%Y%m%d')+'.png'
    plt.savefig(os.path.join(DiffRadarPlots, my_file), bbox_inches='tight', dpi=500)


    df= xr.Dataset({})
    df['Dm_radar']=Dm_radar
    df['temperature']=temperature
    df.Dm_radar.attrs['units']='mm'
    df.Dm_radar.attrs['long_name']='mass weighted mean equivolume diameter in mm'
    
    outPutFileName=pathOutputData+date.strftime('%Y%m%d')+'_Dm_radar_comparison_TempFilt.nc'
    if os.path.exists(outPutFileName):os.remove(outPutFileName)
    df.to_netcdf(pathOutputData+date.strftime('%Y%m%d')+'_Dm_radar_comparison_TempFilt.nc')
    print(pathOutputData+date.strftime('%Y%m%d')+'_Dm_radar_comparison_TempFilt.nc')


except TypeError:
    logger.info('no Dm_radar data on '+date.strftime('%Y%m%d'))
