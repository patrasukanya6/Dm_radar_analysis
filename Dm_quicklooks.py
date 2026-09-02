"""Generate daily radar Dm quicklooks and comparison products.

The script is invoked with seven positional command-line arguments::

    python Dm_quicklooks.py SCRIPT_NAME DATE AVERAGING_MINUTES \
        OUTPUT_DIR DISDROMETER_DIR PLOT_DIR Final_output_DIR


``DATE`` selects the processing day and ``AVERAGING_MINUTES`` controls the
time window used for radar and Parsivel median, minimum, and maximum values.
The workflow downloads the Munich Cloudnet classification product, maps it to
a 4-second and 36-meter reference grid, and retains drizzle/rain pixels. It
then calculates radar mass-weighted mean equivolume diameter (Dm) and PSD
width (sigma_m) from the X-band minus W-band dual-Doppler velocity.

avg_min : the time in minutes over which the radar and Parsivel Dm are averaged to produce a median, minimum, and maximum value for the comparison plot.  The default is 5 minutes.

pathOutputData : the directory where radar resampled data and CloudNet classification data are saved

pathDisdrometer : the directory where Parsivel data are saved

DiffRadarPlots : the directory where the Dm comparison plots are saved

pathDmData_classificationfilter : the directory where the Dm and sigma_m data are saved after filtering with CloudNet classification data

The script creates radar Dm quicklook plots, a CFAD, and a NetCDF product. If
Parsivel data are available, their filtered Dm statistics are overlaid on the
comparison plot and stored in the same NetCDF file. Without Parsivel data,
the radar product is still saved and the absence is logged.

The processing runs at import time because command-line arguments are read
immediately. `
"""

import psutil
import shutil
from sys import argv
import create_cmap as ccm
import os
from HTI_PLOT_general_final import HTI_plot
import xarray as xr
import pandas as pd
import numpy as np
import matplotlib as mpl
import shutil
from Dm_Calculation import Dm_Cal 
import requests
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
import glob
from xticklabels_calculation import xticklabels_calc

import smtplib
smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_username = 'patrasukanya6'
smtp_password = 'xxye veqb xyff qrti'
 
from_email = 'patrasukanya6@gmail.com'
to_email = 'patrasukanya6@gmail.com'

#scriptname,date,avg_min,pathOutputxmacsData, pathOutputwmacsData,emptyDataPath,pathDisdrometer,pathOutputData, DiffRadarPlots= argv 
scriptname,date,avg_min, pathOutputData,pathDisdrometer, DiffRadarPlots , pathDmData_classificationfilter= argv
from matplotlib.colors import LinearSegmentedColormap


date = pd.to_datetime(date)
date1=date.strftime('%Y-%m-%d')

def warning_email(subject,body):
    """Send a processing notification through the configured SMTP server."""
    message = f'Subject: {subject}\n\n{body}'
    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(smtp_username, smtp_password)
        smtp.sendmail(from_email, to_email, message)

import logging
#start = time.time()
#print(start)
# Output log file
logfile = '/home/m/met-actris/scripts/actris/quicklooks/Resample_Data/Dm_radar_pars.log'

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

#start = time.time()
#print(start)
#print("start")

logger.info('Dm calculation starts')

####------------------------------download classificastion files from Cloudnet for DM calculations in the rain region------------------
logger.info('Downloading classification data from CloudNet site')

# Download the daily Cloudnet classification file used to identify rain.
url = 'https://cloudnet.fmi.fi/api/files'
payload = {
    'date': date1,
    'product': 'classification',
    'site':'munich' 
}
metadata = requests.get(url, payload).json()
for row in metadata:
    res = requests.get(row['downloadUrl'])
    with open(pathOutputData+row['filename'], 'wb') as f:
        f.write(res.content)

#except:logger.info('no cloudnet classificaton data')
#process = psutil.Process()
#print(process.memory_info().rss)

#####--------------------------------HTI plot of mean mass weighted diameter----------

logger.info('interpolating classification data into radar data format')


# Align classification data with the radar grid used for the Dm retrieval.
fileNameClass = date.strftime('%Y%m%d')+'_munich_classification.nc'
fnclass= ('/').join([pathOutputData, fileNameClass])
dataset_class=xr.open_dataset(fnclass)#,chunks={'time':5000})
#Z94.where(dataset['target_classification']==3)
##-------------------dataset_class.target_classification.definition
##======='\nValue 0: Clear sky.\nValue 1: Cloud liquid droplets only.\nValue 2: Drizzle or rain.\nValue 3: Drizzle or rain coexisting with cloud liquid droplets.\nValue 4: Ice particles.\nValue 5: Ice coexisting with supercooled liquid droplets.\nValue 6: Melting ice particles.\nValue 7: Melting ice particles coexisting with cloud liquid droplets.\nValue 8: Aerosol particles, no cloud or precipitation.\nValue 9: Insects, no cloud or precipitation.\nValue 10: Aerosol coexisting with insects, no cloud or precipitation.'


print(len(np.where(dataset_class['target_classification']==2)[0]))
if len(np.where(dataset_class['target_classification']==2)[0])!=0:  ## checking if it is a rainy day or not; if it is a rainy day, then only Dm calculation is done; otherwise, it will skip the Dm calculation and will create a quicklook with no rain
    #logger.info('finding the maximum height for which rain exists ')
    #max_ht=np.nanmax(dataset_class.height[np.where(dataset_class['target_classification']==2)[1]].values)-538
    #max_ind=np.abs(dataset10.range.values - max_ht).argmin()
    #logger.info('keeping DDV only upto that height (to reduce calculation time)')
    #ddv_10_94=ddv_10_94[:,:max_ind]

    # Cloudnet heights are AMSL; add the MIM station elevation to define the
    # radar reference grid from 538 m to 12+538 km AMSL.
    beginRangeRef = 0+538 # starting height of the ref grid
    endRangeRef = 12000+538#dataset10.range[max_ind].values+538 # ending height of the ref grid
    rangeFreq = 36 # range resolution of the ref grid
    rangeTolerance = 18 # tolerance for detecting the closest neighbour
    rangeRef = np.arange(beginRangeRef, endRangeRef, rangeFreq)

    timeTolerance = '2S'
    timeFreq = '4S'
# getting the time reference grid
    timeRef = pd.date_range(date, date+pd.offsets.Day(1)-pd.offsets.Second(1), freq=timeFreq)

    dataset_class=dataset_class.reindex({'height':rangeRef},method='nearest')#,tolerance=rangeTolerance)
    dataset_class=dataset_class.reindex({'time':timeRef},method='nearest')#,tolerance=timeTolerance)
#dataset_class=dataset_class.rename({'height':'range'})


    # Load vertically pointing W-band and X-band radar moments for the day.
    logger.info('using wmacs radar data ')
    fileName94 = date.strftime('%Y%m%d')+'_mom_W-band_ZEN.nc'#'_W-band_l1.nc'
    #fn94=('/').join([pathOutputwmacsData,date.strftime('%Y'), date.strftime('%m'),date.strftime('%d')      , fileName94])
    fn94=('/').join([pathOutputData, fileName94])
    dataset94=xr.open_dataset(fn94)
    Z94=dataset94['Ze']
    V94=dataset94['MDV']
    logger.info('using xmacs radar data ')
    fileName10 = date.strftime('%Y%m%d')+'_mom_X-band.nc'#'_W-band_l1.nc'
    #fn10= ('/').join([pathOutputxmacsData, date.strftime('%Y'), date.strftime('%m'),date.strftime('%d'),fileName10])
    fn10=('/').join([pathOutputData,fileName10])
    dataset10=xr.open_dataset(fn10)
    Z10=dataset10['Zg']
    V10=dataset10['VELg']

    # Convert the two radar mean Doppler velocities to the positive DDV
    # convention expected by the polynomial retrieval below.
    logger.info('DDV calculation')
    ddv_10_94=xr.DataArray(V10.values-V94.values)
    ddv_10_94.name='DDV_10_94'
    ddv_10_94=(-1)*ddv_10_94
    ddv_10_94=ddv_10_94.rename({'dim_0':'time','dim_1':'range'})
    logger.info('filtering DDV for rain')
    ddv_10_94=ddv_10_94.where(dataset_class['target_classification'].values<=3)## 2 is for drizzle or rain
    print(len(np.where(~np.isnan(ddv_10_94))[0]))

    if len(np.where(~np.isnan(ddv_10_94))[0])>100:  ## this value is kept after testing for cases with small duration of rain; if the number of non-nan values is less than 100, then it is not considered for Dm calculation

        logger.info('calculating Dm')

        # Apply the sixth-order calibration polynomial published for the
        # X/W-band DDV retrieval, then discard nonphysical negative Dm values.
        Dm_radar= -0.0037*(ddv_10_94)**6 +0.054*(ddv_10_94)**5 -0.320*(ddv_10_94)**4 +0.924*(ddv_10_94)**3 -1.282*(ddv_10_94)**2 +1.119*(ddv_10_94) +0.556 
        #Dm_radar1=0.009*(ddv_10_94)**5-0.097*(ddv_10_94)**4+0.353*(ddv_10_94)**3-0.499*(ddv_10_94)**2+0.608*(ddv_10_94)+0.661    ##reference from Mroz https://doi.org/10.1029/2019EA000789
        Dm_radar.name='Dm'
        Dm_radar=Dm_radar.where(Dm_radar>0)
        
        sigma_m=-0.00066068*ddv_10_94**6  +0.00878698*ddv_10_94**5 -0.05156907 *ddv_10_94**4 + 0.15432127*ddv_10_94**3  -0.18993037*ddv_10_94**2+ 0.24578075*ddv_10_94 + 0.14333473
        
        logger.info('HTI plot of Dm ')

        HTI_plot(fn94,Dm_radar,row=2,col=1,subplot_pos=1,nan_data='True',pathOutputPlots=DiffRadarPlots)
        
        [xtick,xticklabels]=xticklabels_calc(dataset94)
        plt.gcf()


        Dm_radar['time']=dataset10.time
        Dm_radar_20=Dm_radar[:,20]
        Dm_radar_20[Dm_radar_20<0]=np.nan    
        
        # Summarise the lowest radar gate over the requested time interval for
        # the time-series comparison plot.
        logger.info('calculating median min and max for Dm_radar')
        
        Dm_radar_median=Dm_radar_20.resample(time=avg_min+'min').median(skipna='True')
        Dm_radar_max=Dm_radar_20.resample(time=avg_min+'min').max(skipna='True')
        Dm_radar_min=Dm_radar_20.resample(time=avg_min+'min').min(skipna='True')
        
        logger.info('getting those values ready for plotting.....')

        df_max=pd.DataFrame({'time':Dm_radar_median.time,  'max_value': Dm_radar_max})
        df_min=pd.DataFrame({'time':Dm_radar_median.time,  'min_value': Dm_radar_min})
        df_median=pd.DataFrame({'time':Dm_radar_median.time,  'median_value': Dm_radar_median})
        df_radar = pd.concat([df_median['time'], df_min['min_value'], df_max['max_value'], df_median['median_value']],axis=1)

        logger.info('Dm_radar median min max plot starts...')

        ax=plt.subplot(2,1,1)
        plt.ylabel('Height above ground (km)',fontsize = 15)
        #plt.xlim(11700,15300)
        ax=plt.subplot(2,1,2)
        ax.set_position([0.05,0.50-(((2-1)*0.38)/(2-1)), 0.88, 0.32])
        #plt.plot(Dm_radar['time'],Dm_radar[:,20],marker='o',ls='--',markersize=1,color='purple')
        
        plt.fill_between(
        df_radar['time'],
        df_radar['min_value'],
        df_radar['max_value'],
              # <--- THIS IS THE FIX
        color='gray',
        alpha=0.5,
        label='Min-Max Range radar Dm'
        )
        plt.plot(df_radar['time'], df_radar['median_value'], color='black',label='radar(xmacs-wmacs)_Dm_median')
        plt.xlabel('Time [UTC]',fontsize=14)
        plt.ylabel('Dm (mm)',fontsize=14)
     
        plt.ylim(0,3)
        plt.grid(linestyle='--')
        for axis in ['top','bottom','left','right']:ax.spines[axis].set_linewidth(1.5)
        ax.minorticks_on()
        ax.tick_params('both', length=7, width=1.2, which='major')
        ax.tick_params('both', length=5, width=.8, which='minor')

        plt.xticks(fontsize = 15)#)#,fontweight='bold')
        plt.yticks(fontsize = 15)
        ax.yaxis.set_major_locator(MultipleLocator(1))
        ax.yaxis.set_minor_locator(MultipleLocator(0.2))
        ax.xaxis.set_tick_params(labelleft=True,labelsize=15)

        plt.xlim(Dm_radar.time[0],Dm_radar.time[-1])
        ax.text(0.25,0.95,'average over :'+avg_min+'min',fontsize=12,transform=ax.transAxes,ha="right", va="top")
        [o,oo]=plt.xlim(Dm_radar['time'][0].values,Dm_radar['time'][-1].values)
        ax.set_xticks(np.arange(o,oo,(oo-o)/24))
        ax.set_xticklabels(xticklabels)

        my_path=os.path.abspath(DiffRadarPlots)
        my_file=('Dm_10_94_radar_parsivel_'+date.strftime('%Y%m%d')+'.png')
        plt.savefig(os.path.join(my_path, my_file),bbox_inches='tight',dpi=500)
        print(os.path.join(my_path, my_file))    
    ###-------------Saving the radar Dm into NC file-------------------------------
        # Store the full radar profiles, summary statistics, calibration
        # coefficients, and metadata in the Cloudnet-compatible product.
        logger.info('saving the Dm_radar data ')

        df= xr.Dataset({})
        df.attrs['Conventions'] = "CF-1.11"
        df['Dm_radar']=(('dim_0','dim_1'),Dm_radar.data)
        df['sigma_m_radar']=(('dim_0','dim_1'),sigma_m.data)
        
        df['range']=dataset94['range']
        
        df['range'].attrs['long_name']="height above ground"
        df['range'].attrs['units']="m"
        df['time']=dataset94['time']
        df['Dm_radar'].attrs['coordinates']="time range"
        df['sigma_m_radar'].attrs['coordinates']="time range"
        df['Dm_radar_median']=Dm_radar_median
        df['Dm_radar_min']=Dm_radar_min
        df['Dm_radar_max']=Dm_radar_max
        df['poly_fit_Dm_X_W']=np.array([-0.00372353,  0.05410863, -0.32045004,  0.92419538, -1.28242721,
            1.11914028,  0.55603165])
        df['poly_fit_sigma_m_X_W']=np.array([-0.00066068,  0.00878698, -0.05156907,  0.15432127, -0.18993037,
            0.24578075,  0.14333473])
               
        df['poly_fit_Dm_Ka_W']=np.array([ 0.03389303, -0.14087664, -0.17256411,  1.40999482, -1.94744295,
        1.30203209,  0.53672796])
        df['poly_fit_sigma_m_Ka_W']=np.array([ 0.03126386, -0.23421645,  0.58765208, -0.52398584,  0.09669661,
        0.19577081,  0.13957052])

        
        df['poly_fit_Dm_X_Ka']=np.array([ 0.44680848, -2.47498669,  4.31560206, -2.24319053, -0.7542719 ,
        1.42142277,  1.18423371])
        df['poly_fit_sigma_m_X_Ka']=np.array([ 0.412815  , -2.30381555,  4.43000192, -3.23710318,  0.41689968,
        0.70461294,  0.39003869])


        df['poly_fit_Dm_X_W'].attrs['long_name']='Prefactors of the 6th Polynomial fit of retrieving Dm based on the radar Dual-Doppler velocity (applicable for other combination)'
        df['poly_fit_sigma_m_X_W'].attrs['long_name']='Prefactors of the 6th Polynomial fit of retrieving sigma_m based on the radar Dual-Doppler velocity (applicable for other combination)'


        df.Dm_radar.attrs['units']='mm'
        df.sigma_m_radar.attrs['units']='mm'
        df.Dm_radar.attrs['long_name']='mean mass weighted equivolume diameter for Rain'
        df.sigma_m_radar.attrs['long_name']='mass weighted PSD width'
        
        df= df.rename({'dim_0': 'time','dim_1': 'range'})
        df.Dm_radar_median.attrs['long_name']='median of Dm from radar is calculated over '+avg_min+' min'
        df.Dm_radar_min.attrs['long_name']='minimum value of Dm from radar is calculated over '+avg_min+' min'
        df.Dm_radar_max.attrs['long_name']='maximum value of Dm from radar is calculated over '+avg_min+' min'
        df.Dm_radar_median.attrs['units']='mm'
        df.Dm_radar_min.attrs['units']='mm'
        df.Dm_radar_max.attrs['units']='mm'
     
     ###-------------------------Plotting of the Parsivel Data----------------------------   
        # Add the colocated Parsivel comparison when that day's file exists.
        logger.info('using Parsivel data')
        try:
            fn_disdro=pathDisdrometer+date.strftime('%Y')+'/'+date.strftime('%m')+'/'+date.strftime('%Y')+date.strftime('%m')+date.strftime('%d')+'_parsivel2.nc'
            dataset_disdro=xr.open_dataset(fn_disdro)
            Dm_parsivel= Dm_Cal(date, pathDisdrometer)
            # Keep liquid precipitation only: remove invalid Dm, snow/hail,
            # and measurements taken with a cold instrument housing.
            Dm_parsivel[Dm_parsivel<0]=np.nan

            Dm_parsivel[np.where(dataset_disdro['wawa']>61)]=np.nan  ## to extract the cases for snow and haili
            Dm_parsivel[np.where(dataset_disdro['T_sensor_housing']<=3)]=np.nan
            Dm_parsivel=xr.DataArray(Dm_parsivel)
            Dm_parsivel=Dm_parsivel.assign_coords(dim_0=dataset_disdro.time.values)
            Dm_parsivel=Dm_parsivel.rename({'dim_0':'time'})

            Dm_parsivel_median=Dm_parsivel.resample(time=avg_min+'min').median(skipna='True')
            Dm_parsivel_min=Dm_parsivel.resample(time=avg_min+'min').min(skipna='True')
            Dm_parsivel_max=Dm_parsivel.resample(time=avg_min+'min').max(skipna='True')


            df_parsivel_max = pd.DataFrame({'time':Dm_parsivel_median.time,  'max_value': Dm_parsivel_max})
            df_parsivel_min = pd.DataFrame({'time':Dm_parsivel_median.time,  'min_value': Dm_parsivel_min})
            df_parsivel_median=pd.DataFrame({'time':Dm_parsivel_median.time,  'median_value': Dm_parsivel_median})
            df_parsivel = pd.concat([df_parsivel_median['time'], df_parsivel_min['min_value'], df_parsivel_max['max_value'], df_parsivel_median['median_value']],axis=1)

            logger.info('Parsivel plotting starts.....')
            
            plt.gcf()
            ax=plt.subplot(2,1,2)

            plt.fill_between(
            df_parsivel['time'],
            df_parsivel['min_value'],
            df_parsivel['max_value'],
                  # <--- THIS IS THE FIX
            color='m',
            alpha=0.3,
            label='Min-Max Range parsivel Dm'
            )

            plt.plot( df_parsivel['time'], df_parsivel['median_value'], 'm',label='parsivel_Dm_median' )
            plt.legend()

            my_path=os.path.abspath(DiffRadarPlots)
            my_file=('Dm_10_94_radar_parsivel_'+date.strftime('%Y%m%d')+'.png')
            plt.savefig(os.path.join(my_path, my_file),bbox_inches='tight',dpi=500)
            print(os.path.join(my_path, my_file))
            
    ####-------------------Saving the Parsivel data along with the radar in the same netCDF file----------------
            logger.info('saving the Dm_parsivel data ')
            df['Dm_parsivel']=Dm_parsivel
            df['Dm_parsivel_median']=Dm_parsivel_median
            df['Dm_parsivel_min']=Dm_parsivel_min
            df['Dm_parsivel_max']=Dm_parsivel_max
            df.Dm_parsivel.attrs['units']='mm'
            df.Dm_parsivel_median.attrs['units']='mm'
            df.Dm_parsivel_min.attrs['units']='mm'
            df.Dm_parsivel_max.attrs['units']='mm'
            
            df['time_parsivel']=dataset_disdro['time']
            df.Dm_parsivel.attrs['long_name']='mean mass weighted diameter (M4/M3) in mm (M:moment)'
            df.Dm_parsivel_median.attrs['long_name']='median of Dm_parsivel is calculated over '+avg_min+' min'
            df.Dm_parsivel_min.attrs['long_name']='minimum value of Dm_parsivel calculated over '+avg_min+' min'
            df.Dm_parsivel_max.attrs['long_name']='maximum value of Dm_parsivel calculated over '+avg_min+' min'    
            df.attrs.update({
        'contact': 'sukanya.patra@lmu.de , stefan.kneifel@lmu.de',
        
        'purpose': 'This file is generated to upload in the CloudNet site',
        
        'location':'Munich',
        
        'latitude':'48.14',
        
        'longitude':'11.57',

        'references':'https://doi.org/10.1029/2019EA000789(Mroz et al 2020) ',
        
        'DDV Sign Convention':'In our radar, negative Doppler Velocity means downwards motion (rain). The polynomial values of Dm retrieval is computed for positive value of DDV,  and hence one needs to change the sign of Dual-Doppler Velocity (DDV) by multiplying with -1 before retrieving Dm. Also, in case of unphysical negative values of  Dm_radar that needs to be removed',
        
        'DDV_Dm_polynomial':'Dm_radar = P6.ddv^6 + P5.ddv^5 +...........+ P1.ddv + P0',
        
        'general_comments':'This file contains profiles of rain mean mass-weighted equivolume diameter (Dm) and mass weighted PSD width (sigma_m) retrieved from vertically pointing X- and W-band dual Doppler mean Doppler velocities (DDV_X_W) using the method described in Mroz et al., ESS, 2020. Note that the polynomial fits applied are slightly different from the original publication but based on the same PSD in-situ dataset and methodology. The rain part is extracted using CloudNet classification data ("product":"classification").For comparison, also the derived PSD parameters from a colocated Parsivel-2 disdrometer are included in this file. For better visualisation of the comparisoon between Parsivel Dm and radar Dm, a sampling window of 5 mins is used to calculate the median , minimum and maximum value.  For the CloudNet users who does not have the same combination alike the MIM site (X and W-band radar), we have also provided polynomial equation for other possible combination (X-Ka) and (Ka-W).This polynomials are provided by Kamil Mroz. The (X-W) band of radar is the preferable combination for the maximum range of retrieved values, whereas the (X-Ka) combination has a lower limit for Dm : 0.8 mm and (Ka-W) combination has a upper limit of 2 mm.'
    })

            #df= df.rename({'dim_0': 'time_parsivel'})
            df.to_netcdf(pathDmData_classificationfilter+date.strftime('%Y%m%d')+'_EquVolDia_rain_radar_10_94_parsivel'+'.nc')
            print(pathDmData_classificationfilter+date.strftime('%Y%m%d')+'_EquVolDia_rain_radar_10_94_parsivel'+'.nc')

        except FileNotFoundError:
            #plt.title('No Parsivel Data for today')
            my_path=os.path.abspath(DiffRadarPlots)
            my_file=('Dm_10_94_radar_parsivel_'+date.strftime('%Y%m%d')+'.png')
            plt.savefig(os.path.join(my_path, my_file),bbox_inches='tight',dpi=500)
            print(os.path.join(my_path, my_file))


            df.attrs.update({
            'contact': 'sukanya.patra@lmu.de , stefan.kneifel@lmu.de',

            'purpose': 'This file is generated to upload in the CloudNet site',

            'location':'Munich',

            'latitude':'48.14',

            'longitude':'11.57',

            'references':'https://doi.org/10.1029/2019EA000789(Mroz et al 2020) ',

            'DDV Sign Convention':'In our radar, negative Doppler Velocity means downwards motion (rain). The polynomial values of Dm retrieval is computed for positive value of DDV,  and hence one needs to change the sign of Dual-Doppler Velocity (DDV) by multiplying with -1 before retrieving Dm. Also, in case of unphysical negative values of  Dm_radar that needs to be removed',

            'DDV_Dm_polynomial':'Dm_radar = P6.ddv^6 + P5.ddv^5 +...........+ P1.ddv + P0',

            'general_comments':'This file contains profiles of rain mean mass-weighted equivolume diameter (Dm) and mass weighted PSD width (sigma_m) retrieved from vertically pointing X- and W-band dual Doppler mean Doppler velocities (DDV_X_W) using the method described in Mroz et al., ESS, 2020. Note that the polynomial fits applied are slightly different from the original publication but based on the same PSD in-situ dataset and methodology. The rain part is extracted using CloudNet classification data ("product":"classification"). For comparison, also the derived PSD parameters from a colocated Parsivel-2 disdrometer are included in this file. For better visualisation of the comparisoon between Parsivel Dm and radar Dm, a sampling window of 5 mins is used to calculate the median , minimum and maximum value.  For the CloudNet users who does not have the same combination alike MIM site (X and W-band radar), we have also provided polynomial equation for other possible combination (X-Ka) and (Ka-W).This polynomials are provided by Kamil Mroz. The (X-W) band of radar is the preferable combination for the maximum range of retrieved Dm values, whereas the (X-Ka) combination has a lower limit for Dm : 0.8 mm and (Ka-W) combination has a upper limit of 2 mm.'
    })


            df.to_netcdf(pathDmData_classificationfilter+date.strftime('%Y%m%d')+'_EquVolDia_rain_radar_10_94'+'.nc')
            print(pathDmData_classificationfilter+date.strftime('%Y%m%d')+'_EquVolDia_rain_radar_10_94'+'.nc')

            logger.info('No Parsivel data')

         ###-----------------------CFAD of radar retrieved Dm--------------------------------   

        # Build a height/diameter frequency distribution for the radar Dm
        # profiles and display it as a CFAD quicklook.
        logger.info('Dm CFAD is started')
        
        diameter_bins = np.linspace(-1,2,200)
        heights=Dm_radar.range/1000
        height_res = heights[1] - heights[0]
        height_bins = heights - height_res/2
        height_bins= np.append(height_bins, height_bins[-1] + height_res)

        hist, xedges, yedges = np.histogram2d(
                np.array(Dm_radar).T.flatten(),
                np.repeat(heights, Dm_radar.shape[0]),
                bins=[diameter_bins, heights]
        )
        import matplotlib.colors as colors
        hist = hist.T
        
        # Calculate sum of each row and reshape for division
        row_max = hist.max(axis=1, keepdims=True)

        # Divide and multiply by 100 (using np.where to avoid 0/0 error)
        hist_norm = np.divide(hist * 100, row_max, where=row_max!=0)
        hist[hist<5]=np.nan
        norm = colors.LogNorm(vmin=np.nanmin(hist)+ 1, vmax=np.nanmax(hist))
        cmap = 'turbo'
        print(np.nanmean(Dm_radar))
        fig, ax = plt.subplots()
        cfad = ax.imshow(hist, origin='lower', cmap=cmap, aspect='auto',
                    extent=[diameter_bins[0], diameter_bins[-1],
                            heights[0], heights[-1]], norm=norm)

        # add a colorbar
        cbar = fig.colorbar(cfad, ax=ax)
        cbar.set_label('Frequency')
        plt.ylim(0,4)
        plt.xlim(0,2)
        # add labels and title
        ax.set_xlabel('Dm_10_94 (mm)')
        ax.set_ylabel('Height (km)')
        ax.set_title(' CFAD of Mass weighted mean equivolume diameter on'+date.strftime('%Y%m%d'))
        plt.grid(linestyle='--')
        my_path=os.path.abspath(DiffRadarPlots)
        my_file=('Dm_radar_CFAD_'+date.strftime('%Y%m%d')+'.png')
        plt.savefig(os.path.join(my_path, my_file),bbox_inches='tight',dpi=500)
        print(os.path.join(my_path, my_file))
        logger.info('Dm CFAD is done')
        
        ##-------- not saving the CFAD data for time being, but can be saved in the future if needed

        #df['Dm_hist']=(('height_bins','diameter_bins'),hist)
        #df['diameter_bins']=diameter_bins[:-1]
        #df['height_bins']=height_bins[1:-1]
        
        #df.to_netcdf(pathDmData_classificationfilter+date.strftime('%Y%m%d')+'_EquVolDia_rain_radar_10_94_parsivel'+'.nc')
        #print(pathDmData_classificationfilter+date.strftime('%Y%m%d')+'_EquVolDia_rain_radar_10_94_parsivel'+'.nc')
    # If fewer than the minimum number of valid DDV pixels were found, create
    # a diagnostic plot instead of attempting the Dm retrieval and NetCDF
    # export.
    else:
        plt.figure(figsize=(12, 4))
        plt.title('No rain cases on'+date.strftime('%Y%m%d'))
        my_path=os.path.abspath(DiffRadarPlots)
        my_file=('Dm_10_94_radar_parsivel_'+date.strftime('%Y%m%d')+'.png')
        plt.savefig(os.path.join(my_path, my_file),bbox_inches='tight',dpi=500)
        print(os.path.join(my_path, my_file))
        logger.info('No Diameter Plot on'+str(date))

    # This branch is reached when the classification product contains no
    # rain pixels at all, so no radar comparison can be calculated.
else:
    plt.figure(figsize=(12, 4))
    plt.title('No rain cases on'+date.strftime('%Y%m%d'))
    my_path=os.path.abspath(DiffRadarPlots)
    my_file=('Dm_10_94_radar_parsivel_'+date.strftime('%Y%m%d')+'.png')
    plt.savefig(os.path.join(my_path, my_file),bbox_inches='tight',dpi=500)
    print(os.path.join(my_path, my_file))
    logger.info('No Diameter Plot on '+str(date))

##process = psutil.Process()
#print(process.memory_info().rss)
logger.info('Dm Plot ends')

