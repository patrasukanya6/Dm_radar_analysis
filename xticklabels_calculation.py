import numpy as np
def xticklabels_calc(dataset):
	TIME_i=['00:00','01:00','02:00','03:00','04:00','05:00','06:00','07:00','08:00','09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00','19:00',
	'20:00','21:00','22:00','23:00']
	
	Time1=dataset['time'].values
	TIME=list(map(lambda x:x.astype(str)[11:16],Time1))
	TIME=np.array(TIME)
	ind_i=[]
	for i in TIME_i:ind_i.append(np.where(TIME==i)[0][0])
	xtick=ind_i
	xticklabels=list(map(lambda x:x[:2],TIME_i))
	return xtick,xticklabels