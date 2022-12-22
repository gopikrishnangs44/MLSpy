import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd
import h5py

def interp_fun(lat,lon,data):
    lat,lon,data = np.array(lat),np.array(lon),np.array(data)
    nlat = np.arange(-90,90.5,0.5)
    nlon = np.arange(-180,180.5,0.5)
    pp = pd.DataFrame(np.zeros((361,721)))
    for i,j,k in zip(lat, lon, data):
        if k!=0:
            j1,i1 = int(((round(j*2)/2)+180)*2), int(((round(i*2)/2)+90)*2)
            if pp.iloc[i1,j1] == 0 :
                pp.iloc[i1,j1] = k
            else:
                pp.iloc[i1,j1] = (pp.iloc[i1,j1] + k)/2
        else:
            pass
    daa = xr.DataArray(pp, coords=[nlat,nlon], dims=['lat','lon'])
    daa = daa.where(daa!=0 ,np.nan)
    return daa

def mls_o3_profile(fil, time):
    oo = []
    nlat = np.arange(-90,90.5,0.5)
    nlon = np.arange(-180,180.5,0.5)
    levs = [261.0157,215.4435,177.8279,146.7799,121.1528,100,82.54042,68.1292,56.23413,46.41589,38.31187,31.62278,26.10157,21.54435,
           17.78279,14.67799,12.11528,10,8.254042,6.812921,5.623413,4.641589,3.831187,3.162278,2.610157,2.154435,1.778279,1.467799,
           1.211528,1,0.6812921,0.4641589,0.3162278,0.2154435,0.1467799,0.1,0.04641589,0.02154435 ]
    dd = h5py.File(fil, mode='r')
    for i in range(7,45):
        print(levs[i-7])
        data = pd.DataFrame(dd['HDFEOS/SWATHS/O3/Data Fields/L2gpValue'][:,i],columns=['data'])
        data[data == -3.0e-9] == np.nan
        lon = pd.DataFrame(dd['HDFEOS/SWATHS/O3/Geolocation Fields/Longitude'][:],columns=['lon'])
        lat = pd.DataFrame(dd['HDFEOS/SWATHS/O3/Geolocation Fields/Latitude'][:],columns=['lat'])
        qua = pd.DataFrame(dd['HDFEOS/SWATHS/O3/Data Fields/Quality'][:],columns=['qua'])
        pre = pd.DataFrame(dd['HDFEOS/SWATHS/O3/Data Fields/L2gpPrecision'][:,i],columns=['pre'])
        sta = pd.DataFrame(dd['HDFEOS/SWATHS/O3/Data Fields/Status'][:],columns=['sta'])
        con = pd.DataFrame(dd['HDFEOS/SWATHS/O3/Data Fields/Convergence'][:],columns=['con'])
        sza = pd.DataFrame(dd['HDFEOS/SWATHS/O3/Geolocation Fields/SolarZenithAngle'][:],columns=['sza'])
        lst = pd.DataFrame(dd['HDFEOS/SWATHS/O3/Geolocation Fields/LocalSolarTime'][:],columns=['lst'])
        data.loc[qua['qua'] < 1] = np.nan
        data.loc[con['con'] > 1.03] = np.nan
        sta1 = (sta['sta'].mod(2).eq(0)) 
        data.loc[sta1 != True] = np.nan
        data.loc[pre['pre'] < 0] = np.nan
        if time=='day':
            data.loc[sza['sza'] > 89] = np.nan
        elif time=='night':
            data.loc[sza['sza'] < 89] = np.nan
        else:
            pass
        df = np.concatenate((lon,lat,data), axis=1)
        ddd = pd.DataFrame(df, columns=['lon', 'lat', 'data'])   
        final_dat = ddd.groupby(['lat','lon']).mean().reset_index() 
        aj = interp_fun(final_dat['lat'], final_dat['lon'], final_dat['data'])
        oo.append(aj)
    mm = xr.DataArray(oo, coords=[levs, nlat, nlon], dims=['levs','lat','lon'])
    oo = []
    return mm
