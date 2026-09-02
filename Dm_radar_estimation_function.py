import psutil
import shutil
from sys import argv
import os
import xarray as xr
import pandas as pd
import numpy as np
import matplotlib as mpl
import shutil
import requests
import matplotlib.pyplot as plt
import glob
import smtplib


def Dm_radar_estimation(date,pathOutputData):

    date = pd.to_datetime(date)
    date1=date.strftime('%Y-%m-%d')


    #####------------------HTI plot of wmacs moments-------------------------
    fileName94 = date.strftime('%Y%m%d')+'_mom_W-band_ZEN.nc'
    fn94= ('/').join([pathOutputData, fileName94])
    dataset94=xr.open_dataset(fn94)
    V94=dataset94['MDV']



#####------------------HTI plot of 3 radars xmacs , kamacs, and wmacs------------------------

    fileName10 = date.strftime('%Y%m%d')+'_mom_X-band.nc'
    fn10= ('/').join([pathOutputData, fileName10])
    dataset10=xr.open_dataset(fn10)
    V10=dataset10['VELg']

    #####------------------HTI plot of differences of the radars------------------------
    ddv_10_94=xr.DataArray(V10.values-V94.values)
    ddv_10_94.name='DDV_10_94'
    ddv_10_94=(-1)*ddv_10_94


#####--------------------------------HTI plot of mean mass weighted diameter----------



    Dm_radar= -0.0037*(ddv_10_94)**6 +0.054*(ddv_10_94)**5 -0.320*(ddv_10_94)**4 +0.924*(ddv_10_94)**3 -1.282*(ddv_10_94)**2 +1.119*(ddv_10_94) +0.556 
    #Dm_radar1=0.009*(ddv_10_94)**5-0.097*(ddv_10_94)**4+0.353*(ddv_10_94)**3-0.499*(ddv_10_94)**2+0.608*(ddv_10_94)+0.661    ##reference from Mroz https://doi.org/10.1029/2019EA000789
    Dm_radar.name='Dm'
    Dm_radar=Dm_radar.where(Dm_radar>=0)

    df= xr.Dataset({})
    df['Dm_radar']=(('dim_0','dim_1'),Dm_radar.data)
    df['range']=dataset94['range']
    df['time']=dataset94['time']
    df.Dm_radar.attrs['units']='mm'
    df.Dm_radar.attrs['long_name']='mass weighted mean equivolume diameter in mm'
    df= df.rename({'dim_0': 'time','dim_1': 'range'})
    df.to_netcdf(pathOutputData+date.strftime('%Y%m%d')+'_EquVolDia_radar_10_94_for_earthcare.nc')
    print(pathOutputData+date.strftime('%Y%m%d')+'_EquVolDia_radar_10_94_for_earthcare.nc')

    return df

