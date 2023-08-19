# Import libraries
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import time
import os
from functools import partial
import datetime as dt
from calendar import monthrange
from tcpyPI import pi
def _preprocess(x,level):
    return x.sel(level=level)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--year", type=int, required=True, help="year of choice")
args_dict = parser.parse_args()
year_desired = args_dict.year

# importing sys
import sys
# adding Folder_2/subfolder to the system path
sys.path.insert(0, '/glade/u/home/acheung/TCGenesisIndex/Scripts')
from useful_functions import era_5_datestrings,generate_pathstrs
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


start = time.time()

# Open all total column water vapor datasets (W)

data_interval = 1 # days
date_range_list = era_5_datestrings(data_interval,'pl',year_desired)

# Generate path strings for W
variable_id_1 = '133_q' # for specific humidity
all_path_strs_1 = generate_pathstrs(date_range_list,variable_id_1,'sc','pl')

# datasets = xr.open_mfdataset(all_path_strs_1, parallel=True) # Units: kg/m^2

#------------------------------------------------------------------------------------------
# Produce saturation water vapor path strings(W*)... we actually don't use these strings to open a file, but it helps with naming below
date_range_list_2 = era_5_datestrings(data_interval,'pl',year_desired)

# Generate path strings for T
variable_id_2 = '130_t' # for T

all_path_strs_2 = generate_pathstrs(date_range_list_2,variable_id_2,'sc','pl')

# Create file base names for CRH and SD. They both stay the same, so we can just use index 0.
variable_file_name_base_crh = all_path_strs_1[0][57:79] + 'crh.'+all_path_strs_1[0][81:89]+str(data_interval) + 'd_mean.' # We just use the title for both
variable_file_name_base_sd = all_path_strs_1[0][57:79] + 'sd.'+all_path_strs_1[0][81:89]+str(data_interval) + 'd_mean.' # We just use the title for both


es0 = 6.11 #hPa
Lv = 2.501 * 10 **6 #J/kg
Rv = 461 # J/kg/K
T0 = 273 # K
eps = 0.62197

level =  [70.,  100.,  125.,  150.,  175.,  200.,  225.,  250.,  300.,  350.,
        400.,  450.,  500.,  550.,  600.,  650.,  700.,  750.,  775.,  800.,
        825.,  850.,  875.,  900.,  925.,  950.,  975., 1000.] # hPa

partial_func = partial(_preprocess, level=level)

scratch_directory = '/glade/scratch/acheung/'

import dask
dask.config.set({"array.slicing.split_large_chunks": False})

for begin_ind in np.arange(0,len(all_path_strs_2),data_interval):


    #----------------Calculate W*-------------------------------------------------------
    
    # Identify the filepaths for all T files to be opened
    current_path_strs_2 = all_path_strs_2[begin_ind:begin_ind+data_interval] # loop this!
    
    # Identify the start and end strings for the filepath (used later for saving)
    variable_file_name_start_time = current_path_strs_2[0][89:99]
    variable_file_name_end_time = current_path_strs_2[-1][99:]
    
    # Open a week of T data
    datasets_2 = xr.open_mfdataset(current_path_strs_2, preprocess=partial_func, parallel=True,chunks={'time': 24})['T'] # Units: K

    # Calculate saturation vapor pressures using CC equation

    # es = es0 * np.exp((Lv/Rv) * ((1/T0)-(1/datasets_2))) # Units: hPa
    T1 = datasets_2.mean('time').load() - 273.15 # Units: C

    es = 611.2*np.exp(17.67*T1/(T1 + 243.5)) # Units: Pa
    
    # qs =  Epsilon*es / (pressure - (1 - Epsilon)*es);

    qs = (eps*es)/((T1.level*100) - ((1-eps)*es)) # Units: kg/kg
    
    
    # Calculate saturation specific humidity
    # spec_sat = ((es * 0.622)/(datasets_2.level*100 - ((1-0.622)*es)))
#     spec_sat = (0.622 * es)/(datasets_2.level - (0.378 * es))
#     spec_sat = spec_sat.assign_coords({"beg":np.asarray(datasets_2['time'][0])})
#     spec_sat = spec_sat.assign_coords({"end":np.asarray(datasets_2['time'][-1])})

#     # Integrate specific saturation humidity by levels and take time interval mean (W_star)
#     # THESE UNITS ARE not right???!!!
    
    # W_star = qs[9:].integrate("level")
    W_star = qs.sum('level')

#     W_star = W_star.assign_coords({"beg":np.asarray(datasets_2['time'][0])})
#     W_star = W_star.assign_coords({"end":np.asarray(datasets_2['time'][-1])})
    
    #----------------Calculate W-------------------------------------------------------

    #  Since W files are monthly, the lines below determine which W files are needed for the requsted dates in range from W*
    
#     final_time = variable_file_name_end_time[1:11]
#     week_end_dt = dt.datetime.strptime(final_time, '%Y%m%d%H')
#     week_start_dt = dt.datetime.strptime(variable_file_name_start_time, '%Y%m%d%H')

#     months_needed = [week_start_dt.month,week_end_dt.month]
#     months_needed_uniq = np.unique(months_needed)
#     years_needed = [week_start_dt.year,week_end_dt.year]

#     # May be one or two strings

#     path_strs_needed = [] # This is a list of string(s) needed to open, sometimes one or two files if crossing months
    
#     for str_now in range(0,len(months_needed_uniq)):
#         current_str_month = str(months_needed[str_now])
#         if months_needed[str_now] < 10:
#             current_str_month = '0' + current_str_month
        
#         current_str_year = str(years_needed[str_now])
#         current_days_in_month = str(monthrange(int(current_str_year), int(current_str_month))[1])


#         generate_current_datestrs = '/glade/collections/rda/data/ds633.0/e5.oper.an.sfc/'+current_str_year+current_str_month+'/'+'e5.oper.an.sfc.128_137_tcwv.ll025sc.'+current_str_year+current_str_month+'0100_'+current_str_year+current_str_month+current_days_in_month+'23.nc'
#         path_strs_needed.append(generate_current_datestrs) # Append the filepaths that are needed
    
#     # Using the pathstrings we determined above, we open the monthly files(s)
    
#     datasets = xr.open_mfdataset(path_strs_needed, parallel=True) # Units: K
#     TCWV = datasets['TCWV'].sel(time=slice(week_start_dt,week_end_dt)) # loop this!


#    #-------------------------------------Changing code to use specific humidity--------------------------------------------
    current_path_strs_1 = all_path_strs_1[begin_ind:begin_ind+data_interval] # loop this!
    datasets = xr.open_mfdataset(current_path_strs_1,preprocess=partial_func, parallel=True,chunks={'time': 24})['Q'] # Units: kg/kg
    q = datasets.mean('time').load()
    # W = q[9:].integrate("level")
    W = q.sum('level')
    # W = W.assign_coords({"beg":np.asarray(datasets['time'][0])})
    # W = W.assign_coords({"end":np.asarray(datasets['time'][-1])})
#    #-----------------------------------------------------------------------------------------------------------

#     # Find mean W
#     # mean_TCWV = TCWV.mean('time')
#     # mean_TCWV = mean_TCWV.assign_coords({"beg":np.asarray(TCWV['time'][0])})
#     # mean_TCWV = mean_TCWV.assign_coords({"end":np.asarray(TCWV['time'][-1])})

    SD = W - W_star
    CRH = W/W_star
    
    #-------------------------------------Save CRH----------------------------------------------------------------------
    CRH = CRH.assign_coords({"beg":np.asarray(datasets['time'][0])})
    CRH = CRH.assign_coords({"end":np.asarray(datasets['time'][-1])})
    path_crh = "/glade/scratch/acheung/CRH/"
    # Check whether the specified path exists or not
    isExist = os.path.exists(path_crh)
    if not isExist:
    # Create a new directory because it does not exist
        os.makedirs(path_crh) 

    var_file_name_full_crh = variable_file_name_base_crh + variable_file_name_start_time + variable_file_name_end_time
    print(var_file_name_full_crh)
    CRH.to_dataset(name='Column Relative Humidity').to_netcdf(path_crh+'/'+var_file_name_full_crh)
    
    #------------------------------Save Saturation Deficit------------------------------------------------------------
    SD = SD.assign_coords({"beg":np.asarray(datasets['time'][0])})
    SD = SD.assign_coords({"end":np.asarray(datasets['time'][-1])})
    path_sd = "/glade/scratch/acheung/SD/"
    # Check whether the specified path exists or not
    isExist = os.path.exists(path_sd)
    if not isExist:
    # Create a new directory because it does not exist
        os.makedirs(path_sd) 

    var_file_name_full_sd = variable_file_name_base_sd + variable_file_name_start_time + variable_file_name_end_time # We use the start and end times from CRH because they are the same anyways
    print(var_file_name_full_sd)
    SD.to_dataset(name='Saturation Deficit').to_netcdf(path_sd+'/'+var_file_name_full_sd)

# end time
end = time.time()

# total time taken
print(f"Runtime of the program is {end - start}")