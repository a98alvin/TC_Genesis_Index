import xarray as xr
import numpy as np
import os
import time
from functools import partial

def _preprocess(x,level):
    return x.sel(level=level)

import sys
# adding Folder_2/subfolder to the system path
sys.path.insert(0, '/glade/u/home/acheung/TC_Genesis_Index/Scripts')
from useful_functions import era_5_datestrings,generate_pathstrs

from ncar_jobqueue import NCARCluster
from dask.distributed import Client
import dask
cluster = NCARCluster(project='UMCP0022')
cluster.adapt(minimum_jobs=1, maximum_jobs=60)
client = Client(cluster)

data_interval = 7 # days
date_range_list = era_5_datestrings(data_interval,'pl')

# Generate path strings for u
variable_id_1= '131_u' # for relative vorticity
all_path_strs_1 = generate_pathstrs(date_range_list,variable_id_1,'uv','pl')

# Generate path strings for v
variable_id_2= '132_v' # for relative vorticity
all_path_strs_2 = generate_pathstrs(date_range_list,variable_id_2,'uv','pl')

# Choose pressure levels (must be small to large)
level = [200,850] # hPa
partial_func = partial(_preprocess, level=level)
iteration = 1

for begin_ind in np.arange(0,len(all_path_strs_1),data_interval):
    start = time.time()

    current_path_strs_1 = all_path_strs_1[begin_ind:begin_ind+data_interval] # loop this!
    current_path_strs_2 = all_path_strs_2[begin_ind:begin_ind+data_interval]

    # Open u and v together
    datasets = xr.open_mfdataset(current_path_strs_1 + current_path_strs_2,preprocess=partial_func, chunks={'time': 14},parallel=True)
    datasets_mean = datasets.mean('time').load()
    u_shear = datasets_mean['U'].sel(level = 200) - datasets_mean['U'].sel(level = 850)
    v_shear = datasets_mean['V'].sel(level = 200) - datasets_mean['V'].sel(level = 850)
    mean_shear = np.sqrt((u_shear**2) + (v_shear**2))
    mean_shear = mean_shear.assign_coords({"beg":np.asarray(datasets['time'][0])})
    mean_shear = mean_shear.assign_coords({"end":np.asarray(datasets['time'][-1])})
    mean_shear = mean_shear.assign_coords({"lower_level":np.asarray(datasets['level'][-1])})
    mean_shear = mean_shear.assign_coords({"upper_level":np.asarray(datasets['level'][0])})


    # Save deep-layer shear
    path = "/glade/scratch/acheung/dl_shear/"
    # Check whether the specified path exists or not
    isExist = os.path.exists(path)
    if not isExist:
    # Create a new directory because it does not exist
        os.makedirs(path) 


    variable_file_name_base = current_path_strs_1[0][57:79] + 'DL_shear.'+current_path_strs_1[0][81:89]+str(data_interval) + 'd_mean.'
    variable_file_name_start_time = current_path_strs_1[0][89:101]
    variable_file_name_end_time = current_path_strs_1[-1][101:]

    var_file_name_full = variable_file_name_base + variable_file_name_start_time + variable_file_name_end_time

    mean_shear.to_dataset(name='Deep-Layer Shear').to_netcdf(path+'/'+var_file_name_full)
    
    end = time.time()
    print(f"Runtime of week {iteration} of {len(np.arange(0,len(all_path_strs_1),data_interval))} is {round(end - start,2)} s")
    print(f"Predicted Time Remaining: {round((end - start) * (len(np.arange(0,len(all_path_strs_1),data_interval)) - iteration)/3600,2)} h")
    iteration = iteration + 1