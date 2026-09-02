
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

scriptname,date,pathXBand,pathWBand, pathOutputData,emptyDataPath, pathDisdrometer,DiffRadarPlots= argv 

from matplotlib.colors import LinearSegmentedColormap


date = pd.to_datetime(date)
date1=date.strftime('%Y-%m-%d')

def warning_email(subject,body):
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

try:
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

except:logger.info('no cloudnet classificaton data')
#process = psutil.Process()
#print(process.memory_info().rss)


#####------------------HTI plot of wmacs moments-------------------------
try:
    fileName94 = date.strftime('%Y%m%d')+'_mom_W-band_ZEN.nc'
    fn94= ('/').join([pathOutputData, fileName94])
    dataset94=xr.open_dataset(fn94)

except:
    nan_file=('/').join([emptyDataPath,'WnoData.nc'])
    #os.rename(nan_file,fn10)#to get the date from the file name
    #dataset94=xr.open_dataset(nan_file)
    shutil.copyfile(nan_file,fn94)#to get the date from the file name
#dataset94=xr.open_dataset(fn94)
    body = 'wmacs moments Data Missing!',date.today().strftime("%Y-%m-%d")
    subject = 'No wmacs Data'
    #warning_email(subject,body)

    
dataset94=xr.open_dataset(fn94)
Z94=dataset94['Ze']
V94=dataset94['MDV']

#process = psutil.Process()
#print(process.memory_info().rss)


#####------------------HTI plot of 3 radars xmacs , kamacs, and wmacs------------------------
try:
    fileName10 = date.strftime('%Y%m%d')+'_mom_X-band.nc'
    fn10= ('/').join([pathOutputData, fileName10])
    dataset10=xr.open_dataset(fn10)
except: 
    nan_file=('/').join([emptyDataPath,'XnoData.nc'])
    #os.rename(nan_file,fn10)#to get the date from the file name
    shutil.copyfile(nan_file,fn10)#to get the date from the file name
    dataset10=xr.open_dataset(fn10)
    body = 'xmacs data missing!',date.today().strftime("%Y-%m-%d")
    subject = 'No xmacs data'
    #warning_email(subject,body)
    #fn10='X'+fn10.split('/')[-1]    



dataset10=xr.open_dataset(fn10)
#print(dataset10)
Z10=dataset10['Zg']
V10=dataset10['VELg']

 


#####------------------HTI plot of differences of the radars------------------------

   
ddv_10_94=xr.DataArray(V10.values-V94.values)
ddv_10_94.name='DDV_10_94'
ddv_10_94=(-1)*ddv_10_94


#####--------------------------------HTI plot of mean mass weighted diameter----------


try:
#fn='/project/meteo/work/Sukanya.Patra/MIRA35/20241126_munich_classification.nc'
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
    ddv_10_94=ddv_10_94.rename({'dim_0':'time','dim_1':'range'})
    #ddv_10_94['time']=V94['time']
    ddv_10_94=ddv_10_94.where(dataset_class['target_classification']==2)## 2 is for drizzle or rain
    row1=np.where(dataset_class['target_classification']<4)[0]
    coloumn1=np.where(dataset_class['target_classification']<4)[1]


    Dm_radar= -0.0037*(ddv_10_94)**6 +0.054*(ddv_10_94)**5 -0.320*(ddv_10_94)**4 +0.924*(ddv_10_94)**3 -1.282*(ddv_10_94)**2 +1.119*(ddv_10_94) +0.556 
    #Dm_radar1=0.009*(ddv_10_94)**5-0.097*(ddv_10_94)**4+0.353*(ddv_10_94)**3-0.499*(ddv_10_94)**2+0.608*(ddv_10_94)+0.661    ##reference from Mroz https://doi.org/10.1029/2019EA000789
    Dm_radar.name='Dm'
    
    sigma_m=-0.00066068*ddv_10_94**6  +0.00878698*ddv_10_94**5 -0.05156907 *ddv_10_94**4 + 0.15432127*ddv_10_94**3  -0.18993037*ddv_10_94**2+ 0.24578075*ddv_10_94 + 0.14333473

    miu=(Dm_radar**2/sigma_m**2)-4
    D=np.arange(0,4,0.1)
    lambdaa=miu+4/Dm_radar
    #ND=np.zeros((D.shape[0],Z10.shape[0]))*np.nan


    
    #for j in range(0,Z10.shape[0]):
    #    for i in range(0,334):ND[j,i]=np.nansum((D**miu[j,i].values*np.exp(D* (-1* (4+miu[j,i]).values/Dm_radar1[j,i] .values) ) * D**6 * 0.1))
    

    ##for j in range(0,Z10.shape[0]):ND[:,j]=list(map(lambda i : i**miu[j,20]*np.exp(i * (-1* lambdaa) ) * i**6 * 0.1, D  )) 
    ## since, Ze = N0 * ∫ND D**6 dD =∫D**miu * exp(-lambda*D) * D**6 dD 
    
    #N0=np.zeros((Z10.shape[0],Z10.shape[1]))*np.nan
    #for j in range(0,Z10.shape[0]):
    #    for i in range(0,334):N0[j,i]=10**Z10[j,i].values/ND[j,i]
    
    #Dm_radar=Dm_radar.where(Dm_radar>0)    
    HTI_plot(fn94,Dm_radar,row=2,col=1,subplot_pos=1,nan_data='True',pathOutputPlots=DiffRadarPlots)
    
    [xtick,xticklabels]=xticklabels_calc(dataset94)
    plt.gcf()
    ax=plt.subplot(2,1,1)
    plt.ylabel('Height above ground (km)',fontsize = 15)
    #plt.xlim(11700,15300)
    ax=plt.subplot(2,1,2)
    ax.set_position([0.05,0.50-(((2-1)*0.38)/(2-1)), 0.88, 0.32])
    plt.plot(Dm_radar['time'],Dm_radar[:,20],marker='o',ls='--',markersize=1,color='purple')
    
    plt.ylim(0,3)
    plt.grid(linestyle='--')
    for axis in ['top','bottom','left','right']:ax.spines[axis].set_linewidth(1.5)
    ax.minorticks_on()
    ax.tick_params('both', length=7, width=1.2, which='major')
    ax.tick_params('both', length=5, width=.8, which='minor')

    plt.xticks(fontsize = 15)#)#,fontweight='bold')
    plt.yticks(fontsize = 15)#)#,fontweight='bold')i
    #plt.xlim(Dm_radar['time'][11700].values,Dm_radar['time'][15300].values)
    ax.yaxis.set_major_locator(MultipleLocator(1))
    ax.yaxis.set_minor_locator(MultipleLocator(0.2))
    ax.xaxis.set_tick_params(labelleft=True,labelsize=15)
    plt.ylabel('Dm (mm)',fontsize = 15)
    plt.xlabel('Time[UTC]',fontsize = 15)
    plt.legend(['Dm_xmacs_wmacs'])
    [o,oo]=plt.xlim(Dm_radar['time'][0].values,Dm_radar['time'][-1].values)
    ax.set_xticks(np.arange(o,oo,(oo-o)/24))
    ax.set_xticklabels(xticklabels)
    df= xr.Dataset({})
    df['Dm_radar']=(('dim_0','dim_1'),Dm_radar.data)
    df['range']=dataset94['range']
    df['time']=dataset94['time']
    df.Dm_radar.attrs['units']='meter'
    df= df.rename({'dim_0': 'time','dim_1': 'range'})

    
    
    try:
        fn_disdro=pathDisdrometer+date.strftime('%Y')+'/'+date.strftime('%m')+'/'+date.strftime('%Y')+date.strftime('%m')+date.strftime('%d')+'_parsivel2.nc'
        dataset_disdro=xr.open_dataset(fn_disdro)
        [xtick,xticklabels]=xticklabels_calc(dataset94)
        plt.gcf()
        ax=plt.subplot(2,1,2)
        Dm= Dm_Cal(date, pathDisdrometer)
        Dm[Dm<0]=np.nan
        #Dm_radar=Dm_radar.where(Dm_radar>0)
        Dm[np.where(dataset_disdro['wawa']>61)]=np.nan  ## to extract the cases for snow and haili
        Dm[np.where(dataset_disdro['T_sensor_housing']<=3)]=np.nan  
        
        plt.plot(dataset_disdro['time'],Dm ,'o',color='teal')
        plt.legend(('Dm_xmacs_wmacs','Dm_Parsivel'))
       # plt.xlim(Dm_radar['time'][11700],Dm_radar['time'][15300])
        
        plt.rc('legend',fontsize=14)
        my_path=os.path.abspath(DiffRadarPlots)
        my_file=('Dm_10_94_Pasivel_'+date.strftime('%Y%m%d')+'.png')
        plt.savefig(os.path.join(my_path, my_file),bbox_inches='tight',dpi=500)
        print(os.path.join(my_path, my_file))
        df['Dm_parsivel']=Dm
        df.Dm_parsivel.attrs['units']='meter'
        df['time_parsivel']=dataset_disdro['time']
        #df= df.rename({'dim_0': 'time_parsivel'})
        df.to_netcdf(pathOutputData+date.strftime('%Y%m%d')+'_EquVolDia_rain_10_94'+'.nc')
        print(pathOutputData+date.strftime('%Y%m%d')+'_EquVolDia_rain_10_94'+'.nc')
        
        print(Dm.shape,Dm_radar.shape)
       # plt.figure()
        #plt.scatter(Dm,Dm_radar)
        #plt.xlabel('Dm_Disdrometr')
        #plt.ylabel('Dm_6Poly')

        #plt.savefig(os.path.join(my_path, 'scatter_Dm_didro_6Poly.png'),bbox_inches='tight',dpi=500)


        #plt.figure()
        #plt.scatter(Dm,Dm_radar1)
       # plt.xlabel('Dm_Disdrometr')
        #plt.ylabel('Dm_7Poly')
        #plt.savefig(os.path.join(my_path, 'scatter_Dm_didro_7Poly.png'),bbox_inches='tight',dpi=500)
    except FileNotFoundError:
        #plt.title('No Parsivel Data for today')
        my_path=os.path.abspath(DiffRadarPlots)
        my_file=('Dm_10_94_Pasivel_'+date.strftime('%Y%m%d')+'.png')
        plt.savefig(os.path.join(my_path, my_file),bbox_inches='tight',dpi=500)
        print(os.path.join(my_path, my_file))
        df.to_netcdf(pathOutputData+date.strftime('%Y%m%d')+'_EquVolDia_rain_10_94'+'.nc')
        logger.info('No Parsivel data')
    #HTI_plot(fn94,Dm,nan_data='True',pathOutputPlots=DiffRadarPlots)
except:
    HTI_plot(fn94,Dm_radar,nan_data='True',pathOutputPlots=DiffRadarPlots)
    #print('plot Dm')
    #body = 'Dm Plot Missing!',date.today().strftime("%Y-%m-%d")
    #subject = 'No Dm plot'
    #warning_email(subject,body)
    
    logger.info('No Diameter Plot on'+date)

##process = psutil.Process()
#print(process.memory_info().rss)
logger.info('Dm Plot ends')
