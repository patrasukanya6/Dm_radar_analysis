

import numpy as np
import xarray as xr
def Dm_Cal(date,pathDisdrometer): #date after doing pd.datetime
	fn_disdro=pathDisdrometer+date.strftime('%Y')+'/'+date.strftime('%m')+'/'+date.strftime('%Y')+date.strftime('%m')+date.strftime('%d')+'_parsivel2.nc'
	dataset_disdro=xr.open_dataset(fn_disdro)



	dia_width=dataset_disdro['dwidth']
	#diameter=dataset_disdro['dclasses']

	diameter=np.array([0.062, 0.187, 0.312, 0.376, 0.496, 0.608, 0.754, 0.869, 1.021, 1.166, 1.348, 1.581, 1.801, 2.022, 2.275, 2.649, 3.085, 3.546, 4.013, 4.708, 		5.50,6.500,7.500, 8.500, 9.5, 11, 13, 15, 17, 19, 21.50, 24.50]) # from Joanathan's thesis, correction for disdrometer diameter
	dia_width=np.append(np.diff(diameter),dia_width[-1])

	N=dataset_disdro['N'].where(dataset_disdro['N']!=-9.999)
	N=10**N #doing the anti log    
	N_corr=(N*dataset_disdro['dwidth'].values)
	N_corr=N_corr/dia_width
    #N_corr=10**N_corr

	A=[]
	B=[]
	Dm=np.ones(N_corr.shape[0])*np.nan
	for i in np.arange(0,N_corr.shape[0]):
		A=(np.array(diameter**3)*np.array(N_corr[i,:])*np.array(dia_width))
		B=(np.array(diameter**4)*np.array(N_corr[i,:])*np.array(dia_width))
		
		Dm[i]=(np.nansum(B)/np.nansum(A))

    #Dm=Dm/1000#from mm to meter conversion

	#Dm[np.where(Dm>10)]=np.nan
	return Dm
