
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import matplotlib.pyplot as plt
import calendar
import xarray as xr
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
import pandas as pd
import math
import os
import datetime
#from suntime import Sun, SunTimeException
import ephem
import matplotlib as mpl

TIME_i=['00:00','01:00','02:00','03:00','04:00','05:00','06:00','07:00','08:00','09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00','19:00',
'20:00','21:00','22:00','23:00']	
def HTI_plot(fn,Input,**args):	

	
	
	#Vmin,Vmax,colormap=inspect.getargspec(func)
	dataset=xr.open_dataset(fn)
	title=fn.split('/')[-1].split('.')[0]

	try:
		args["pathOutputPlots"]
		pathOutputPlots=args["pathOutputPlots"]
		#print('ananya')
	except:pathOutputPlots='/home'
	
	
	try: 
		#args["colormap"]
		colormap=args["colormap"]
	except:colormap='turbo'
	
	try:
		args["Vmax"]
		Vmax=args["Vmax"]
		Vmin=args["Vmin"]
	except:
		if Input.name=='Ze' or Input.name=='Z'or Input.name=='sZg' or Input.name=='Zg':
			Vmax=30
			Vmin=-50
		elif Input.name=='Ze' and 'W' in title:
			try:
				args['diff_radar']
				Vmax=30;Vmin=-50
			except:Vmax=20;Vmin=-50
		elif Input.name=='Ze' and 'mrr' in title:
			Vmax=60
			Vmin=-20
		elif Input.name=='SW' or Input.name=='WIDTH' or Input.name=='RMSg'or Input.name=='sRMSg':
			Vmax=1
			Vmin=0
		elif Input.name=='LDR' or Input.name=='sLDR' or Input.name=='sLDR_w' or Input.name=='LDRg' or Input.name[0:4]=='DLDR':
			Vmax=-5
			Vmin=-35
			
		elif Input.name=='MDV':
			try:
				args['diff_radar']
				Vmax=3
				Vmin=-5	
			except:
				Vmax=3
				Vmin=-5	

		elif Input.name=='VEL' or Input.name=='VELg' or Input.name=='sVELg':
			try:
				args['diff_radar']
				Vmax=3
				Vmin=-5	
			except:
				Vmax=3
				Vmin=-8	

		#elif Input.name=='sVELg':
		#	Vmax=0
		#	Vmin=-3	
		
		elif Input.name=='V':
			Vmax=2
			Vmin=-6
		elif Input.name=='LWC':
			Vmax=1
			Vmin=0
		elif Input.name=='RR':
			Vmax=20
			Vmin=0
			
		elif Input.name=='SKWg' or Input.name=='SK' or Input.name=='Sk':
			Vmax=1
			Vmin=-1
		elif Input.name=='rc_signal':
			Vmax=-4
			Vmin=-7
			
	#print(Vmax)
		
	
		
	time_notation=[]
	if 'Days' in dataset.coords:time_notation='Days'
	else: time_notation='[UTC]'
	
	if time_notation=='Days':
		xtick=np.arange(24,Input.shape[0]+24,24)
		xticklabels=np.arange(1,len(xtick)+1)#dataset['days'].values
		input1=Input
	elif time_notation=='[UTC]' and 'Nan_Data' in title:
		input1=Input
		Time1=dataset['time'].values
		TIME=list(map(lambda x:x.astype(str)[11:16],Time1))
		TIME=np.array(TIME)
		#date=fn[-21:-13]
		#xtick=np.arange(0,input1.shape[0],1000)
		#xticklabels=[]	
		
		
	if time_notation=='[UTC]' and 'W' in title:
		Ze=dataset['Ze']
		Time1=dataset['time'].values
		date=fn[-26:-18]
		try: 	
			args['nan_data']
			input1=Input
			Time2=Time1
			#xtick=np.arange(0,input1.shape[0],1000)
			#xticklabels=TIME[0:input1.shape[0]:1000]
		except:
			input1=Input[~np.isnan(Ze).all(axis=1),:]
			Time2=Time1[~np.isnan(Ze).all(axis=1)]

			#xtick=np.arange(0,input1.shape[0],500)
			#xticklabels=TIME[0:input1.shape[0]:500]
			
		TIME=list(map(lambda x:x.astype(str)[11:16],Time2))
		TIME=np.array(TIME)			


		
	elif time_notation=='[UTC]' and 'Ka' in title:
		Time1=dataset['time'].values
		date=fn[-23:-15]
		TIME=list(map(lambda x:x.astype(str)[11:16],Time1))
		TIME=np.array(TIME)
		input1=Input
		#xtick=np.arange(0,input1.shape[0],1000)
		#xticklabels=TIME[0:input1.shape[0]:1000]

	elif time_notation=='[UTC]' and 'X' in title:
		Time1=dataset['time'].values
		date=fn[-22:-14]
		TIME=list(map(lambda x:x.astype(str)[11:16],Time1))
		TIME=np.array(TIME)
		input1=Input
		
	elif time_notation=='[UTC]' and 'mrr' in title:
		Time1=dataset['time'].values
		TIME=Time1
		input1=Input
		date=fn[-21:-13]
		
		
	elif time_notation=='[UTC]' and 'ceilometer' in title:
		Time1=dataset['time'].values
		TIME=Time1
		input1=Input
		date=fn[-28:-20]
		#xtick=np.arange(0,input1.shape[0],1000)
		#xticklabels=Time1[0:input1.shape[0]:1000]
	try:
		args['diff_radar']
		if 'X' in title:TITLE='xmacs'
		elif 'Ka' in title:TITLE='kamacs'
		else:TITLE='wmacs'
		#print(TITLE)
	except:print('')
	try:
		args['met_schau']
		ind_i=[]
		for i in TIME_i[::2]:ind_i.append(np.where(TIME==i)[0][0])
		ind_i.append(len(TIME))
		xtick=ind_i
		xticklabels=list(map(lambda x:x[:2],TIME_i[::2]))
		xticklabels.append('24')
	except:
		ind_i=[]
		for i in TIME_i:ind_i.append(np.where(TIME==i)[0][0])	
		xtick=ind_i
		xticklabels=list(map(lambda x:x[:2],TIME_i))	

	time=np.ones((input1.shape[1],input1.shape[0]))*np.arange(0,input1.shape[0])
	if 'range' in dataset.coords:ht='range'
	else:ht='height'

	#if input1.name =='Dm':height=np.ones((input1.shape[0],input1.shape[1]))*dataset[ht][:74].values/1000
	#else:height=np.ones((input1.shape[0],input1.shape[1]))*dataset[ht].values/1000
	height=np.ones((input1.shape[0],input1.shape[1]))*dataset[ht].values/1000
	
	if input1.name=='Ze' or input1.name=='Zg' or input1.name=='Z' or input1.name=='sZg':ColorbarLabel='Z$_e$(dBZ$_e$)'
	#if input1.name=='sZg':ColorbarLabel='Slanted Z$_e$(dBZ$_e$)'
	if input1.name=='SW' or input1.name=='WIDTH' or input1.name=='RMS'or input1.name=='RMSg' or input1.name=='sRMSg':ColorbarLabel='SW (m$^{-1}$)'
	#if input1.name=='sRMSg':ColorbarLabel='Slanted SW (m$^{-1}$)'
	if input1.name=='V' or input1.name=='MDV' or input1.name=='VEL'or input1.name=='VELg' or input1.name=='sVELg':ColorbarLabel='Vel(ms$^{-1}$)'
	#if input1.name=='sVELg':ColorbarLabel='Slanted Vel(ms$^{-1}$)'
	if input1.name=='LDR'or input1.name=='LDRg' or input1.name=='sLDR':ColorbarLabel='slanted LDR(dB)'
	#elif input1.name=='sLDR_w':ColorbarLabel='Slanted LDR(dB)'
	if input1.name=='RR':ColorbarLabel='Rain Rate (mm h$^{-1}$)'
	if input1.name=='LWC':ColorbarLabel='LWC (gm m$^{-3}$)'
	if input1.name=='SKWg' or input1.name=='SK' or input1.name=='Sk':ColorbarLabel='Skewness'
	if input1.name=='rc_signal':ColorbarLabel='log(rc_signal) @1064 nm'
	if input1.name=='ZDR':
		ColorbarLabel='ZDR(dB)'
		try:
			args["Vmax"]
			Vmax=args["Vmax"]
			Vmin=args["Vmin"]
		except:
			Vmax=4
			Vmin=-1
	if input1.name=='KDP':
		ColorbarLabel='KDP(°km$^{-1}$)'
		try:
			args["Vmax"]
			Vmax=args["Vmax"]
			Vmin=args["Vmin"]
		except:
			Vmax=4
			Vmin=-1
			
	if input1.name=='RHV':
		ColorbarLabel='RhoHV'
		try:
			args["Vmax"]
			Vmax=args["Vmax"]
			Vmin=args["Vmin"]
		except:
			Vmax=1
			Vmin=0.85
			
	if input1.name=='sZDRmax':
		ColorbarLabel='sZDR$_m$$_a$$_x$(dB)'
		try:
			args["Vmax"]
			Vmax=args["Vmax"]
			Vmin=args["Vmin"]
		except:
			Vmax=4
			Vmin=-1
			
	if input1.name[:3]=='DWR':
		unitt='(dB)'
		try:
			args["Vmax"]
			Vmax=args["Vmax"]
			Vmin=args["Vmin"]
		except:
			Vmax=10
			Vmin=-5
	if input1.name[:3] in ['DDV' , 'DSW']:
		unitt='(ms$^{-1}$)'
		try:
			args["Vmax"]
			Vmax=args["Vmax"]
			Vmin=args["Vmin"]
		except:
			Vmax=0.3
			Vmin=-0.3
	if input1.name=='Dm':
		ColorbarLabel='Dm (mm)'
		try:
			args["Vmax"]
			Vmax=args["Vmax"]
			Vmin=args["Vmin"]
		except:
			Vmax=2
			Vmin=0


	#print(Vmax)
	if input1.name[:3]=='DSK':
		unitt=''
		try:
			args["Vmax"]
			Vmax=args["Vmax"]
			Vmin=args["Vmin"]
		except:
			Vmax=1
			Vmin=-1



	if input1.name[3:]=='_35_94':
		ColorbarLabel=input1.name[:3]+'$_3$$_5$$_-$$_9$$_4$'+unitt
	if input1.name[3:]=='_10_35':
		ColorbarLabel=input1.name[:3]+'$_1$$_0$$_-$$_3$$_5$'+unitt
	if input1.name[3:]=='_10_94':
		ColorbarLabel=input1.name[:3]+'$_1$$_0$$_-$$_9$$_4$'+unitt




	if input1.name=='DLDR_35_94':
		ColorbarLabel='DLDR$_3$$_5$$_-$$_9$$_4$(dB)'




	try : 
		
		row=args['row']
		col=args['col']
		#total_subplots=args['total_subplots']
		subplot_pos=args['subplot_pos']
		#print(subplot_pos)
		if col==1:
			#
			#fig.canvas.manager.set_window_title('My Window Title')
			#plt.figure('My Window Title')
			if subplot_pos==1:
				try:
					args["figsize"]
					fig, ax = plt.subplots(row,col,figsize=args["figsize"])
					#print('sukanya')
				except:fig, ax = plt.subplots(row,col,figsize=(15,10))
			else:fig=plt.gcf()
			ax=plt.subplot(row,col,subplot_pos)
			if row==4:ax.set_position([0.05,0.76-(((subplot_pos-1)*0.70)/(row-1)), 0.88, 0.21])##0.76 is the position of the subplot can start and the total space width is 0.70
			elif row==3:ax.set_position([0.05,0.68-(((subplot_pos-1)*0.60)/(row-1)), 0.88, 0.26])
			elif row==2:ax.set_position([0.05,0.50-(((subplot_pos-1)*0.38)/(row-1)), 0.88, 0.32])
                        #elif row==2:print('row is 2');ax.set_position([0.05,0.50-(((subplot_pos-1)*0.38)/(row-1)), 0.95, 0.32])
			#print()

	except:
		try:
			args['met_schau']
			fig,ax=plt.subplots(1,1,figsize=(60.3,16.48)) #85.12,18.98
			#fig.subplots_adjust(left=0.027, bottom=0.08, right=1.12, top=0.963) #0.9018
			ax.set_position([0.126,0.12, .867, 0.77])
		except:
			fig, ax = plt.subplots(figsize=(15,6))
			ax.set_position([0.09,0.10, .84, 0.75])#.88,.85
	

	
	#calculation of sunrise and sunset timeHT
	Munich=ephem.Observer()
	try:
		date
		Munich.date=pd.to_datetime(date).strftime('20%y/%m/%d %H:%M:%S')
		Munich.lon='11.57'
		Munich.lat='48.13'
		sun=ephem.Sun()
		d_ss=str(Munich.next_setting(sun))
		d_sr=str(Munich.next_rising(sun))
		D_ss=pd.to_datetime(d_ss)
		D_sr=pd.to_datetime(d_sr)
		sr_hm=D_sr.strftime('%H:%M')
		ss_hm=D_ss.strftime('%H:%M')
		ind1=np.where(TIME==sr_hm)
		#print(ind1)
		if len(ind1[0])!=0: 
			try: 
				args['met_schau']
				if 'ceilometer' in title:plt.plot(np.ones((height.shape[1]))*ind1[0][0],height[0,:],'w',linestyle='dashed',linewidth=7)
				else:plt.plot(np.ones((height.shape[1]))*ind1[0][0],height[0,:],'k',linestyle='dashed',linewidth=7)
			except:plt.plot(np.ones((height.shape[1]))*ind1[0][0],height[0,:],'k',linestyle='dashed')
		ind2=np.where(TIME==ss_hm)
		if len(ind2[0])!=0:
			try: 
				args['met_schau']
				if 'ceilometer' in title:plt.plot(np.ones((height.shape[1]))*ind2[0][0],height[0,:],'w',linestyle='dashed',linewidth=7)
				else:plt.plot(np.ones((height.shape[1]))*ind2[0][0],height[0,:],'k',linestyle='dashed',linewidth=7)
			except:
				plt.plot(np.ones((height.shape[1]))*ind2[0][0],height[0,:],'k',linestyle='dashed')
				if 'ceilometer' in title:plt.plot(np.ones((height.shape[1]))*ind2[0][0],height[0,:],'w',linestyle='dashed',linewidth=7)
	except:
		ind1=[['ACTRIS']]
		ind1[0]=[]
		ind2=[['ACTRIS']]
		ind2[0]=[]
		print('No data has been plotted')
	##------Main pcolor plot------------
	#print(input1.name)



	pc=ax.pcolor(time.transpose(),height,input1,vmin=Vmin,vmax=Vmax,cmap=colormap)
	#pc=plt.imshow(RC_Signal.T,cmap='jet',vmin=Vmin,vmax=Vmax,aspect='auto',origin='lower', extent=[timelines[0], timelines[-1], heightrange[0], heightrange[-1]])
	
	#cbaxes1=fig.add_axes([0.96, 0.14, 0.015, 0.75])
	#cb1=plt.colorbar(plot,cax = cbaxes1,ticks=[4.2,5.2,6.2,7.2])
	
	#if 'mrr' or 'ceilometer' in title:
	if	(np.nanmean(dataset['nan_index'])!=0):

	#if dataset['nan_index'].all()!=0:
		try:
			args['met_schau']
			#plt.axvspan(dataset['nan_index'][0].values, input1.shape[0], facecolor='whitesmoke', alpha=0.8)
			plt.axvspan(dataset['nan_index'][0].values, dataset['nan_index'][-1].values, facecolor='whitesmoke', alpha=0.8)
		except:#plt.axvspan(dataset['nan_index'][0].values, input1.shape[0], facecolor='lightgrey', alpha=0.8)
			plt.axvspan(dataset['nan_index'][0].values, dataset['nan_index'][-1].values, facecolor='lightgrey', alpha=0.8)
	ax.set_xticks(xtick)
	try: 
		args['met_schau']
		#ax.set_yticklabels(np.arange(0,13))
		plt.grid(color='k',linestyle='--',linewidth=2)
		plt.xlim(0,input1.shape[0])
		#plt.ylim(height[1,0],height[1,-1])
	except:
		plt.grid(linestyle='--')
		plt.xlim(0,input1.shape[0])
		
		
	for axis in ['top','bottom','left','right']:ax.spines[axis].set_linewidth(1.5)
	ax.minorticks_on()
	ax.tick_params('both', length=7, width=1.2, which='major')
	ax.tick_params('both', length=5, width=.8, which='minor')
	box_text = "Kamacs= -1\nWmacs=-1.5\nxmacs=-5"
	if args.get('offset_corrected') or args.get('offset_corrected_zoom'):
		if subplot_pos==1:
			ax.text(
			0.98, 0.98, box_text,
			transform=ax.transAxes,
			fontsize=14,
			verticalalignment='top',
			horizontalalignment='right',
			bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
	
	


	if 'met_schau' in args:
		#args['met_schau']
		plt.xticks(fontsize = 38)
		plt.yticks(fontsize =38)
		ax.yaxis.set_major_locator(MultipleLocator(1))
		ax.yaxis.set_minor_locator(MultipleLocator(0.5))
	elif 'offset_corrected_zoom' in args:
		plt.ylim(0,1)
		ax.yaxis.set_major_locator(MultipleLocator(0.4))
		ax.yaxis.set_minor_locator(MultipleLocator(0.2))
		plt.xticks(fontsize = 15)#)#,fontweight='bold')
		plt.yticks(fontsize = 15)
	else:
		plt.xticks(fontsize = 15)#)#,fontweight='bold')
		plt.yticks(fontsize = 15)#)#,fontweight='bold')
		ax.yaxis.set_major_locator(MultipleLocator(2))
		ax.yaxis.set_minor_locator(MultipleLocator(1))
	#plt.ylim(0,6)
	if (np.nanmax(height)<5):	
	#if  ('offset_corrected_zoom' in args) or (input1.name=='Dm'):
		ax.yaxis.set_major_locator(MultipleLocator(0.4))
		ax.yaxis.set_minor_locator(MultipleLocator(0.2))

	#except:print('')
	try: 
		args['row']#and args['offset_corrected_zoom']!='True':
	#if args['row'] and args['offset_corrected_zoom'] is None:
		#print('chudi giri bondho koro')
		if subplot_pos==row:
			
			ax.set_xticklabels(xticklabels)
			ax.xaxis.set_tick_params(labelleft=True,labelsize=15)
			if len(ind1[0])!=0:
				if('mrr' in title or row==2 or 'offset_corrected_zoom' in args):ax.text(ind1[0][0],-.5,'sunrise',fontsize = 15, ha='center')#,fontweight='bold')#-2.9i,, 'mrr' in title or
				#elif 'offset_corrected_zoom' in args:print('2nd elif command');ax.text(ind1[0][0]-400,-1.5,'sunrise',fontsize = 15)
                
				else:print('3rd else command');ax.text(ind1[0][0]-200,-2.9,'sunrise',fontsize = 15)
			#trans = mtrans.blended_transform_factory(ax.transData, ax.transAxes)            
			if len(ind2[0])!=0:
				if('mrr' in title or row==2 or 'offset_corrected_zoom' in args):ax.text(ind2[0][0], -.5, 'sunset', fontsize=15,  ha='center')  #ax.text(ind2[0][0]-200,-1.5,'sunset',fontsize = 15)#'mrr' in title 
				#elif 'offset_corrected_zoom' in args:ax.text(ind2[0][0]-100,-1.5,'sunset',fontsize = 15)
				else:ax.text(ind2[0][0]-200,-2.9,'sunset',fontsize = 15)#,fontweight='bold')
			#if len(ind1[0])!=0 and row!=2:ax.text(ind1[0][0]-200,-2.9,'sunrise',fontsize = 10)#,fontweight='bold')#-2.9
			#if len(ind2[0])!=0 and row!=2:ax.text(ind2[0][0]-200,-2.9,'sunset',fontsize = 10)#,fontweight='bold')

			if time_notation=='Days':plt.xlabel('Time'+'('+time_notation+')',fontsize=18)#,fontweight='bold')
			else:plt.xlabel('Time'+time_notation,fontsize=18)#,fontweight='bold')					
			if 'mrr' in title:my_file=('MRR_variables_'+date+'.png')
			if 'X' in title:my_file=('xmacs_HTI_Z_V_SW_LDR_'+date+'.png')
			if 'Ka' in title and time_notation=='Days':my_file=('kamacs_Moments_'+date+'.png')
			if 'Ka' in title and time_notation=='[UTC]':my_file=('kamacs_HTI_Z_V_SW_LDR_'+date+'.png')
			if input1.name in ['ZDR' , 'ZDRmax' , 'KDP' , 'RHV']:my_file=('wmacs_HTI_ZDR_KDP_sZDRmax_RhoHV_'+date+'.png')
			if 'ZEN' in title and 'W' in title:my_file=('wmacs_HTI_Z_V_SW_LDR_'+date+'.png')
			if 'ceilometer' in title:my_file=('Ceilometer_RC_Signal_'+fn[-28:-20]+'.png')
			if input1.name in ['sZg' , 'sRMSg' , 'sVELg' , 'sLDR_w']  and 'CEL' in title:my_file=('wmacs_slanted_HTI_Z_V_SW_LDR_'+date+'.png')
			if input1.name[-5:]=='10_35':my_file=(date+'_'+input1.name.split('_')[0]+'.png')
			if input1.name[-5:]=='35_94':my_file=(date+'_'+input1.name.split('_')[0]+'.png')
			if input1.name[-5:]=='10_94':my_file=(date+'_'+input1.name.split('_')[0]+'.png')
			try:
				args['diff_radar']
				#print('Ananya')
				my_file=('X_Ka_wmacs_'+input1.name+'_'+date+'.png')
				#print('my_file')
			except:print('')
			'''
			try:
				#[args['nan_data'] and args['diff_radar']]
				args['diff_radar']
				if row == 3:
					plt.title('wmacs',fontsize=18)#,fontweight='bold')
					ax.annotate('xmacs on '+date,xy=(0.4,0.96), xycoords='figure fraction',fontsize=18,fontweight='bold',rotation='horizontal')
					ax.annotate('kamacs',xy=(0.45,0.65), xycoords='figure fraction',fontsize=18,fontweight='bold',rotation='horizontal')
				#my_file=('X_Ka_wmacs_'+input1.name+'_'+date+'.png')
					my_file=(date+'_'+input1.name+'.png')
				else:
					plt.title('wmacs',fontsize=18)#,fontweight='bold')
					ax.annotate('xmacs on '+date,xy=(0.4,0.96), xycoords='figure fraction',fontsize=18,fontweight='bold',rotation='horizontal')
					ax.annotate('kamacs',xy=(0.45,0.65), xycoords='figure fraction',fontsize=18,fontweight='bold',rotation='horizontal')
				#my_file=('X_Ka_wmacs_'+input1.name+'_'+date+'.png')
					my_file=(date+'_'+input1.name+'.png')
			except:print('')
			'''
			#print(my_file)		
		else:
			ax.xaxis.set_tick_params(labelleft=False)

		if subplot_pos==1:
			#ax.annotate('Height above ground (km)',xy=(.001,0.4), xycoords='figure fraction',fontsize=18,rotation='vertical')
			if input1.name=='Dm':plt.ylim(0.5,4);plt.title('Mean mass-weighted equivolume diameter on '+date,fontsize=18);plt.ylabel('Height above ground (km)',fontsize = 15)#,fontweight='bold')
			else:ax.annotate('Height above ground (km)',xy=(.001,0.4), xycoords='figure fraction',fontsize=18,rotation='vertical')
            
			try:
				args['diff_radar']
				ax.set_title(TITLE+' on '+date,fontsize=18)#,fontweight='bold')
			except:print('')
			
			if input1.name in ['ZDR',  'ZDRmax' , 'KDP' , 'RHV']:
				plt.title('wmacs Polarimetric Moments on '+date,fontsize=18)#,fontweight='bold')
				
			#if 'ZEN' in title:
			if input1.name in ['Ze',  'MDV' , 'WIDTH' , 'sLDR'] and 'ZEN' in title:
				plt.title('wmacs Moments on '+date,fontsize=18)#,fontweight='bold')
			if input1.name in ['sZg' , 'sRMSg' , 'sVELg' , 'sLDR_w']  and 'CEL' in title:
				plt.title('wmacs (slanted) Moments on '+date,fontsize=18)#,fontweight='bold')
			if 'Ka' in title and input1.name!='Dm':
				if time_notation=='Days':
					mon=title[-6:-4]
					year=title[-4:]
					plt.title(title[:-7]+calendar.month_name[int(mon)]+' '+year,fontsize=18)#,fontweight='bold')
					#my_file=
				else:
					plt.title('kamacs Moments on '+date,fontsize=18)#,fontweight='bold')
			if 'X' in title and input1.name!='Dm':plt.title('xmacs Moments on '+date,fontsize=18)#,fontweight='bold') 	

			if 'mrr' in title:
				plt.title('MRR variables on '+date,fontsize=18)#,fontweight='bold')
				#my_file=('mrr_variables_'+date+'.png')
			#if args['nan_data']=='True':plt.title('xmacs on',fontsize=18)#,fontweight='bold')
			if input1.name[-5:]=='10_35':
				plt.title(date+' '+'xmacs-kamacs',fontsize=18)#,fontweight='bold')
				#print('Ananya')
			if input1.name[-5:]=='35_94':
				plt.title(date+' '+'kamacs-wmacs',fontsize=18)#,fontweight='bold')
				#print('Sukanya')
			if input1.name[-5:]=='10_94':
				plt.title(date+' '+'xmacs-wmacs',fontsize=18)#,fontweight='bold')
				#my_file=(input1.name.split('-')[0]+'_'+date+'.png')			
		else:
			try:
				args['diff_radar']
				#print(TITLE)
				plt.title(TITLE,fontsize=18)#,fontweight='bold')
				#ax.text(12,15,TITLE,fontsize=18)#,fontweight='bold')
				#print('Soma')
			except:
				if input1.name[-5:]=='10_35':
					plt.title('xmacs-kamacs',fontsize=18)#,fontweight='bold')
					
				if input1.name[-5:]=='35_94':
					plt.title('kamacs-wmacs',fontsize=18)#,fontweight='bold')
				
				if input1.name[-5:]=='10_94':
					plt.title('xmacs-wmacs',fontsize=18)#,fontweight='bold')
	
#		if subplot_pos>1:plt.rcParams['xtick.top'] = True
		#if subplot_pos==2 and args['nan_data']=='True':plt.title('kamacs',fontsize=18)#,fontweight='bold'
	except:
	#else:
		ax.set_xticklabels(xticklabels)
		try:
			args['met_schau']
			plt.xlabel('Time'+time_notation,fontsize=38)
			plt.ylabel('Height above ground (km)',fontsize=38)
			if len(ind1[0])!=0 and args['met_schau']:ax.text(ind1[0][0]-100,-.99,'sunrise',fontsize = 38)                                       
			if len(ind2[0])!=0 and args['met_schau']:ax.text(ind2[0][0]-100,-.99,'sunset',fontsize = 38)
		except:
			plt.xlabel('Time'+time_notation,fontsize=18)#,fontweight='bold')
			plt.ylabel('Height above ground [km]',fontsize=18)#,fontweight='bold')

		if len(ind1[0])!=0:ax.text(ind1[0][0]-200,-1.5,'sunrise',fontsize = 12)#,fontweight='bold')
		if len(ind2[0])!=0:ax.text(ind2[0][0]-200,-1.5,'sunset',fontsize = 12)#,fontweight='bold')
		if input1.name=='Dm':
			plt.title('Mean mass-weighted equivolume diameter on '+date,fontsize=18)#,fontweight='bold')
			my_file=(input1.name+'_'+date+'.png')
					
		if 'W' in title:
			date=fn[-26:-18]
			plt.title(input1.name+' '+date,fontsize=18)#,fontweight='bold')
			my_file=(input1.name+'_'+date+'.png')
		#if 'ZEN' and 'W' in title:
		#	plt.title('wmacs '+input1.name+' '+date,fontsize=18)#,fontweight='bold')
		if 'ceilometer' in title:
			plt.title('LMU-MIM, Munich 48.148° N 11.573° E, altitiude: 539 m Lufft CHM15kx (CHM15kxLMU)'+fn[-28:-20]+' firmware: 1.11',fontsize=38)
			my_file=('Ceilometer_RC_Signal_'+fn[-28:-20]+'.png')
			
		if 'Ka' in title:
			if time_notation=='Days':
				mon=title[-6:-4]
				year=title[-4:]
				plt.title(title[:-7]+calendar.month_name[int(mon)]+' '+year,fontsize=18)#,fontweight='bold')
			else:
				#date=fn[-23:-15]
				try:
					args['met_schau']
					#print('sukanya')
					plt.title('Meteorological Institute of Ludwig-Maximilians-Universität (München, Germany, 48.148 N / 11.573 E):  KaMACS: '+date,fontsize=38)
					my_file=('kamacs_met-schau_'+input1.name+'_'+date+'.png')
				except:
					plt.title('kamacs '+input1.name+' '+date,fontsize=18)#,fontweight='bold')	
					my_file=('kamacs_'+input1.name+'_'+date+'.png')
	
		if 'mrr' in title:
			#date=date
			plt.title('mrr '+input1.name+' '+date,fontsize=18)#,fontweight='bold')
			my_file=('mrr_'+input1.name+'_'+date+'.png')


		#print(my_file)

	try:
		args['row'] ###-----calculation of colorbar axis position for subplots----------------------
		if row==4:cbaxes1=fig.add_axes([0.94,0.76-(((subplot_pos-1)*0.70)/(row-1)), 0.015, 0.21])
		elif row==3:cbaxes1=fig.add_axes([0.94,0.68-(((subplot_pos-1)*0.60)/(row-1)), 0.015, .27])#0.22])
		elif row==2:cbaxes1=fig.add_axes([0.94,0.50-(((subplot_pos-1)*0.38)/(row-1)), 0.015, 0.32])
		cb1=plt.colorbar(pc,cax = cbaxes1)
	except:
		try:
			args['met_schau']
			cbaxes1=fig.add_axes([0.955, 0.08, 0.013, 0.87])##-------------------for single plots
			cb1=plt.colorbar(pc,cax = cbaxes1)
			#cb=plt.colorbar(pc,ticks=[4.2,5.2,6.2,7.2])
			#cb1.ax.tick_params(labelsize=38,color=colours[style]['cb'])
			#cb1.set_label('Ze in dBZ',fontsize=38,color=colours[style]['cb'])
			#cb1=plt.colorbar(pc)#,cax = cbaxes1)

		except:
			
			cbaxes1=fig.add_axes([0.94, 0.12, 0.015, 0.72])##-------------------for single plots
			cb1=plt.colorbar(pc,cax = cbaxes1)
	

	try:
		args['met_schau']
		#print('chodu')
		cb1.set_label(ColorbarLabel,fontsize=38)
		for t in cb1.ax.get_yticklabels():t.set_fontsize(38)	
	
	except:		#print('no need of cbaxes1')
	
		if input1.name[:3]=='DDV':	
			norm = mpl.colors.Normalize(Vmin,Vmax)
			cb1 = mpl.colorbar.ColorbarBase(cbaxes1, cmap=colormap,norm=norm)
			axcb = cb1.ax
			for t in cb1.ax.get_yticklabels():
				t.set_fontsize(12)
				#t.set_fontweight('bold')
		else:

			axcb = cb1.ax
			dv=((Vmax-Vmin)/5) # 5 is the number of ticks

			if dv<1 and dv>0.1:
				cb1.set_ticks(np.arange(Vmin,Vmax+dv,dv))
				numbers=(np.arange(Vmin,Vmax+dv,dv))
				labels = list(map(lambda x: math.floor(x*10)/10, numbers))
				cb1.set_ticklabels(labels)
			elif  dv<=0.1:
				dv=math.floor(dv*100)/100
				cb1.set_ticks(np.arange(Vmin,Vmax,dv))
				numbers=(np.arange(Vmin,Vmax,dv))
				labels = list(map(lambda x: math.floor(x*100)/100, numbers))
				cb1.set_ticklabels(labels)
			elif dv>1 and dv<10:	
				cb1.set_ticks(np.arange(Vmin,Vmax+dv,dv))
				numbers=(np.arange(Vmin,Vmax+dv,dv))
				labels = list(map(lambda x: round(x), numbers))
				cb1.set_ticklabels(labels)
			else:	
				cb1.set_ticks(np.arange(Vmin,Vmax+dv,dv))
				dv=round(dv)
				cb1.set_ticklabels(np.arange(Vmin,Vmax+dv,dv))
		

			for t in cb1.ax.get_yticklabels():
				t.set_fontsize(12)
				#t.set_fontweight('bold')
		axcb.tick_params(length=3, width=1.2, which='major')
		cb1.set_label(ColorbarLabel,fontsize=12)#,fontweight='bold')
#plt.savefig('X_ka_W-macs_'+input1.name+'_'+date+'.png',dpi=100)

	try:
		row
		if subplot_pos==row:
			my_path=os.path.abspath(pathOutputPlots)
			#plt.tight_layout()
			try:
				args['offset_corrected']
				my_file=my_file[:-4]+'_LV1'+'.png'
				plt.savefig(os.path.join(my_path, my_file),bbox_inches='tight',dpi=500)
				print(os.path.join(my_path, my_file))
			except:print('')
			try:
				args['offset_corrected_zoom']
				#plt.tight_layout()
				my_file=my_file[:-4]+'_LV1_zoom'+'.png'
				plt.savefig(os.path.join(my_path, my_file),bbox_inches='tight',dpi=500)
				print(os.path.join(my_path, my_file))
			except:
			    my_file=my_file 
			    plt.savefig(os.path.join(my_path, my_file),bbox_inches='tight',dpi=500)
			    print(os.path.join(my_path, my_file))
			#plt.close()
	except:				
		my_path=os.path.abspath(pathOutputPlots)
		#print(my_path)
		#plt.tight_layout()
		try: 
			args['met_schau']
			print('plot is done')
			plt.tight_layout()
			plt.savefig(os.path.join(my_path, my_file),dpi=100)
		except:
			plt.savefig(os.path.join(my_path, my_file),bbox_inches='tight',dpi=500)
			#plt.close()
		print(os.path.join(my_path, my_file))
	#print('----------------------',fn,'is done-----------------')
		
