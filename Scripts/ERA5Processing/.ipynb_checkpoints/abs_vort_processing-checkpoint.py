# Import libraries and functions
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import time
import os
from functools import partial

def _preprocess(x,level):
    return x.sel(level=level)

import sys
# adding Folder_2/subfolder to the system path
sys.path.insert(0, '/glade/u/home/acheung/TC_Genesis_Index/Scripts')
from useful_functions import era_5_datestrings,generate_pathstrs

#-------------NCAR Jobqueue------------------------------------
from ncar_jobqueue import NCARCluster
from dask.distributed import Client
import dask
cluster = NCARCluster(project='UMCP0022')
cluster.adapt(minimum_jobs=1, maximum_jobs=60)
client = Client(cluster)

#-------------Script------------------------------------------


# Open only pressure level 850 hPa
data_interval = 7 # days
date_range_list = era_5_datestrings(data_interval,'pl')
variable_id = '138_vo' # for relative vorticity
all_path_strs = generate_pathstrs(date_range_list,variable_id,'sc','pl')
start = time.time()

level = 850 # hPa
partial_func = partial(_preprocess, level=level)
iteration = 1
# Load weekly data
for begin_ind in np.arange(0,len(all_path_strs),data_interval):

    current_path_strs = all_path_strs[begin_ind:begin_ind+data_interval]
    datasets = xr.open_mfdataset(current_path_strs,preprocess=partial_func, parallel=True,chunks={'time': 14})['VO'].drop('level')
    datasets_mean = datasets.mean('time').load()
    
    # Create array Coriolis Parameter
    omega = 7.292 * 10 **-5 # 1/s
    f = 2*omega*np.sin(np.deg2rad(datasets.latitude))

    # Calculate Absolute Vorticity
    mean_abs_vort_850 = datasets_mean + f
    mean_abs_vort_850 = mean_abs_vort_850.assign_coords({"beg":np.asarray(datasets['time'][0])})
    mean_abs_vort_850 = mean_abs_vort_850.assign_coords({"end":np.asarray(datasets['time'][-1])})

    # Save absolute vorticity
    path = "/glade/scratch/acheung/abs_vort"
    # Check whether the specified path exists or not
    isExist = os.path.exists(path)
    if not isExist:
    # Create a new directory because it does not exist
        os.makedirs(path) 


    variable_file_name_base = current_path_strs[0][57:90] + str(data_interval) + 'd_mean.'
    variable_file_name_start_time = current_path_strs[0][90:101]
    variable_file_name_end_time = current_path_strs[-1][101:]

    var_file_name_full = variable_file_name_base + variable_file_name_start_time + variable_file_name_end_time


    mean_abs_vort_850.to_dataset(name='Absolute Vorticity').to_netcdf(path+'/'+var_file_name_full)
    end = time.time()

    print(f"Runtime of week {iteration} of {len(np.arange(0,len(all_path_strs),data_interval))} is {round(end - start,2)} s")
    print(f"Predicted Time Remaining: {round((end - start) * (len(np.arange(0,len(all_path_strs),data_interval)) - iteration)/3600,2)} h")
    iteration = iteration + 1
    

