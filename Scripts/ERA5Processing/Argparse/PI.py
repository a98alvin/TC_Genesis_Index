import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from datetime import timedelta
import os
import sys
sys.path.insert(0, '/glade/u/home/acheung/TCGenesisIndex/Scripts')
from useful_functions import era_5_datestrings,generate_pathstrs,run_sample_dataset_2, week_to_month
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import time

from ncar_jobqueue import NCARCluster
from dask.distributed import Client
import dask
# Change your url to the dask dashboard so you can see it

cluster = NCARCluster(project='UMCP0022')
cluster.adapt(minimum_jobs=1, maximum_jobs=60)
client = Client(cluster)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--year", type=int, required=True, help="year of choice")
args_dict = parser.parse_args()
year_desired = args_dict.year

# Need to simulate week by week, so we do pressure level strings first, which are daily files

# Need to simulate week by week, so we do pressure level strings first, which are daily files
data_interval = 1 # days
date_range_list_pl = era_5_datestrings(data_interval,'pl',year_desired)

# Generate T file path strings

T_var_id = '130_t'
T_path_strs = generate_pathstrs(date_range_list_pl,T_var_id,'sc','pl')

# Generate specific humidity (q) file path strings

q_var_id = '133_q'
q_path_strs = generate_pathstrs(date_range_list_pl,q_var_id,'sc','pl')

iteration = 1
for i in range(0,len(date_range_list_pl),data_interval):
    start = time.time()

    # Find out what week we are working with here
    week_start_dt = date_range_list_pl[i]
    if i + data_interval >= len(date_range_list_pl):
        week_end_dt = date_range_list_pl[-1]
    else:
        week_end_dt = date_range_list_pl[i+data_interval]
    
    # Find the string needed to open a monthly file for the week for sst
    path_strs_needed_sst = week_to_month(week_start_dt,week_end_dt,'034_sstk','sc')

    # Grab SST (degrees C)

    SSTK_pre = xr.open_mfdataset(path_strs_needed_sst,parallel=True)
    SSTK = SSTK_pre.sel(time=slice(week_start_dt,week_end_dt-timedelta(hours=1))).mean('time')
    
    SSTK.coords['longitude'] = (SSTK.coords['longitude'] + 180) % 360 - 180
    SSTK = SSTK.sortby(SSTK.longitude)
    SSTC = SSTK - 273.15
    SSTC = SSTC.assign_coords({"beg":week_start_dt})
    SSTC = SSTC.assign_coords({"end":week_end_dt-timedelta(hours=1)})
    SSTC = SSTC.drop_vars('utc_date')
    
    # Grab Temperature Soundings
    
    T = xr.open_mfdataset(T_path_strs[i:i+data_interval],parallel=True,chunks={'time': 14}).mean('time')
    T = T.reindex(level=list(reversed(T.level))) - 273.15
    T.coords['longitude'] = (T.coords['longitude'] + 180) % 360 - 180
    T = T.sortby(T.longitude)
    T = T.assign_coords({"beg":week_start_dt})
    T = T.assign_coords({"end":week_end_dt-timedelta(hours=1)})
    T = T.drop_vars('utc_date')
    # Grab MSL
    
    path_strs_needed_msl = week_to_month(week_start_dt,week_end_dt,'151_msl','sc')

    msl_pre = xr.open_mfdataset(path_strs_needed_msl) # Units: Pa
    msl = msl_pre.sel(time=slice(week_start_dt,week_end_dt-timedelta(hours=1))).mean('time')
    msl.coords['longitude'] = (msl.coords['longitude'] + 180) % 360 - 180
    msl = msl.sortby(msl.longitude)
    msl = msl/100 # Units: hPa
    msl = msl.assign_coords({"beg":week_start_dt})
    msl = msl.assign_coords({"end":week_end_dt-timedelta(hours=1)})
    msl = msl.drop_vars('utc_date')

    # Grab Mixing Ratio (g/kg)

    # ASSUMPTION! In the sample data, specific humidity is assumed to be approximately equal to mixing ratio (r), since r/(1+r) = q and r << 1
    
    q = xr.open_mfdataset(q_path_strs[i:i+data_interval],parallel=True,chunks={'time': 14}).mean('time') # Units: kg/kg
    q.coords['longitude'] = (q.coords['longitude'] + 180) % 360 - 180
    q = q.sortby(q.longitude)
    q = q.reindex(level=list(reversed(q.level)))
    
    # Convert to g/kg
    q = q * 1000 # Units: g/kg
    q = q.assign_coords({"beg":week_start_dt})
    q = q.assign_coords({"end":week_end_dt-timedelta(hours=1)})
    q = q.drop_vars('utc_date')

    # total time taken
    current_strs_for_saving = T_path_strs[i:i+data_interval]

    variable_file_name_start_time = current_strs_for_saving[0][89:100]
    variable_file_name_end_time = current_strs_for_saving[-1][100:]

    var_file_name_full = "PI_" + variable_file_name_start_time + variable_file_name_end_time
    
    merged = xr.merge([SSTC,T,msl,q],compat='override')
    ds_1 = run_sample_dataset_2(merged)
    
    path = "/glade/scratch/acheung/PI/"
    # Check whether the specified path exists or not
    isExist = os.path.exists(path)
    if not isExist:
    # Create a new directory because it does not exist
        os.makedirs(path) 

    ds_1['vmax'].to_netcdf(path + var_file_name_full)
    print('...PI computation complete and saved\n')

    end = time.time()
    print(f"Runtime of day {iteration} of {len(np.arange(0,len(T_path_strs),data_interval))} is {round(end - start,2)} s")
    print(f"Predicted Time Remaining: {round((end - start) * (len(np.arange(0,len(T_path_strs),data_interval)) - iteration)/3600,2)} h")
    iteration = iteration + 1