# Import libraries
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import time
import os
from functools import partial
from useful_functions import era_5_datestrings,generate_pathstrs

data_interval = 7 # Range of data to be averaging over
date_range_list = era_5_datestrings(data_interval)
variable_id = '138_vo' # for relative vorticity

all_path_strs = generate_pathstrs(date_range_list,variable_id)

# Open only pressure level 850 hPa
def _preprocess(x,level):
    return x.sel(level=level)

start = time.time()

level = 850 # hPa
partial_func = partial(_preprocess, level=level)

# Load weekly data
for begin_ind in np.arange(0,len(all_path_strs),data_interval):

    current_path_strs = all_path_strs[begin_ind:begin_ind+data_interval]
    datasets = xr.open_mfdataset(current_path_strs,preprocess=partial_func, parallel=True)['VO'].drop('level')
    # Create array Coriolis Parameter
    omega = 7.292 * 10 **-5 # 1/s
    f = 2*omega*np.sin(np.deg2rad(datasets.latitude))

    # Calculate Absolute Vorticity
    abs_vort = datasets + f

    # Calculate interval mean
    mean_abs_vort_850 = abs_vort.mean('time')
    mean_abs_vort_850 = mean_abs_vort_850.assign_coords({"beg":np.asarray(abs_vort['time'][0])})
    mean_abs_vort_850 = mean_abs_vort_850.assign_coords({"end":np.asarray(abs_vort['time'][-1])})

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


    mean_abs_vort_850.to_dataset(name='Absolute Vorticity').to_netcdf('/glade/scratch/acheung/abs_vort/'+var_file_name_full)

# end time
end = time.time()

# total time taken
print(f"Runtime of the program is {end - start}")