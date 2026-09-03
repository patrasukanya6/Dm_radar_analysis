import matplotlib.pyplot as plt

import numpy as np

ddv=np.arange(-0.5,4,0.1)
ddv_10_35=ddv
ddv_10_94=ddv
ddv_35_94=ddv
Dm_radar_35_94=0.0339*(ddv_35_94)**6 -0.141*(ddv_35_94)**5 -0.173*(ddv_35_94)**4 + 1.41*(ddv_35_94)**3 -1.947*(ddv_35_94)**2 + 1.302*(ddv_35_94) +0.537
Dm_radar_10_94= -0.0037*(ddv_10_94)**6 +0.054*(ddv_10_94)**5 -0.320*(ddv_10_94)**4 +0.924*(ddv_10_94)**3 -1.282*(ddv_10_94)**2 +1.119*(ddv_10_94) +0.556
Dm_radar_10_35=0.447*ddv_10_35**6 -2.475*ddv_10_35**5 +4.32*ddv_10_35**4 -2.243*ddv_10_35**3 -0.754*ddv_10_35**2 + 1.421*ddv_10_35 +1.184

sigma_m_10_94=-0.00066068*ddv_10_94**6  +0.00878698*ddv_10_94**5 -0.05156907 *ddv_10_94**4 + 0.15432127*ddv_10_94**3  -0.18993037*ddv_10_94**2+ 0.24578075*ddv_10_94 + 0.14333473


sigma_m_10_35= 0.412815 *ddv_10_35**6  - 2.30381555*ddv_10_35**5 + 4.43000192*ddv_10_35**4  -3.23710318*ddv_10_35**3 + 0.41689968*ddv_10_35**2+ 0.70461294*ddv_10_35 + 0.39003869

sigma_m_35_94=0.03126386*ddv_35_94**6  -0.23421645*ddv_35_94**5 +0.58765208*ddv_35_94**4  -0.52398584*ddv_35_94**3 + 0.09669661*ddv_35_94**2+ 0.19577081*ddv_35_94+ 0.13957052

pathOutputPlots='/project/meteo/homepages/quicklooks/actris/'
plt.figure(figsize=(10,6))
plt.plot(ddv, Dm_radar_10_94,label='X-W')
plt.plot(ddv, Dm_radar_35_94,label='Ka-W')
plt.plot(ddv, Dm_radar_10_35,label='X-Ka')
plt.legend(['X-W','Ka-W','X-Ka'],fontsize=14)
plt.xlabel('DDV (m/s)',fontsize=14)
plt.ylabel('Dm (mm)',fontsize=14)
plt.grid(linestyle='--')
plt.ylim(0,2)
plt.xlim(-.5,2.5)
plt.yticks(fontsize=14)
plt.xticks(fontsize=14)

plt.savefig(pathOutputPlots+'Dm_DDV_plot.png',bbox_inches='tight',dpi=500)

plt.figure(figsize=(12,10))
plt.plot(Dm_radar_10_94,ddv,label='X-W')

plt.plot( Dm_radar_35_94,ddv,label='Ka-W')
#plt.plot( Dm_radar_10_35,ddv,label='X-Ka')
plt.legend(['X-W','Ka-W','X-Ka'])
plt.xlabel('Dm (mm)')
plt.ylabel('DDV (m/s)')
plt.grid(linestyle='--')
plt.ylim(0,2)
plt.xlim(-.5,2.5)
plt.savefig(pathOutputPlots+'Dm_DDV_plot.png',bbox_inches='tight',dpi=500)


plt.figure(figsize=(10,6))
plt.plot(ddv, sigma_m_10_94,label='X-W')
plt.plot(ddv, sigma_m_35_94,label='Ka-W')
#plt.plot(ddv, sigma_m_10_35,label='X-Ka')
plt.legend(['X-W','Ka-W'],fontsize=14)
plt.xlabel('DDV (m/s)',fontsize=14)
plt.ylabel('sigma_m (mm)',fontsize=14)
plt.yticks(fontsize=14)
plt.xticks(fontsize=14)

plt.grid(linestyle='--')
plt.xlim(-.5,2.5)
plt.ylim(0,1)
plt.savefig(pathOutputPlots+'sigma_m_DDV_plot.png',bbox_inches='tight',dpi=500)


