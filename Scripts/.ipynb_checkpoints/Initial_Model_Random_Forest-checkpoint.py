import numpy as np
import xarray as xr
from useful_functions import data_compiler
from useful_functions import month_genesis_locs
from useful_functions import grid_counter
from useful_functions import environmental_select_stack
from useful_functions import create_genesis_grid_labels
from useful_functions import take_closest_point
from distance import distance_calculator
from distance import pointdist_calc
import os
import tropycal.tracks as tracks
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import matplotlib.pyplot as plt
import warnings
import cartopy.crs as ccrs

warnings.simplefilter(action='ignore', category=FutureWarning)

# Compile Environmental Data
vars_list = os.listdir("/glade/work/acheung/TC_Genesis") # Determine Variables
vars_list.remove('.DS_Store')
vars_list.remove('CRH_ERA5')
all_vars_list = []
for vars_list_now in vars_list:
    Varcompiled, YearList,lons,lats,arr = data_compiler(vars_list_now)
    all_vars_list.append(Varcompiled)

arr = xr.DataArray(all_vars_list,coords=[("Variable",vars_list),("Year",range(1950,2021)),("Latitude",lats),("Longitude",lons),("Month",range(1,13))])

# # Time ranges for EVERYTHING desired
month_range = np.arange(1,13,1)
test_years = np.arange(2005,2021,1)
train_years = np.arange(1950,2005,1)
train_years = np.setdiff1d(train_years, np.arange(1971,1979,1))
Latitude=np.arange(0,80,2)
Longitude=np.arange(260,360,2)

train_stacked,train_NaNlocs = environmental_select_stack(month_range,train_years,Latitude,Longitude,arr)
test_stacked,test_NaNlocs = environmental_select_stack(month_range,test_years,Latitude,Longitude,arr)

train_env_data = train_stacked.drop_isel(z=train_NaNlocs).transpose()
test_env_data = test_stacked.drop_isel(z=test_NaNlocs).transpose()

#--------------------------------------------------------------------------------------------------------
# # Grab ibtracs data (uncomment this section if you want to recreate genesis (observed) labels, otherwise it is already saved)
# basin_dataset = tracks.TrackDataset(basin='north_atlantic',source='ibtracs',include_btk=True)

# # Create genesis labels from ibtracs data (slowest step)
# vmin=0
# print('Training Dataset')
# train_labels_predropped = create_genesis_grid_labels(month_range,train_years,vmin,basin_dataset)
# print('Testing Dataset')
# test_labels_predropped = create_genesis_grid_labels(month_range,test_years,vmin,basin_dataset)

# train_labels_predropped.unstack().to_dataset(name='Genesis_Grids').to_netcdf("/glade/work/acheung/Initial_RF_Datasets/train_labels_predropped.nc")
#test_labels_predropped.unstack().to_dataset(name='Genesis_Grids').to_netcdf("/glade/work/acheung/Initial_RF_Datasets/test_labels_predropped.nc")
#--------------------------------------------------------------------------------------------------------

# Read in already created genesis (obs) labels
train_labels_predropped_read = xr.open_dataset("/glade/work/acheung/Initial_RF_Datasets/train_labels_predropped.nc")
train_labels_predropped = train_labels_predropped_read.stack(z=("Month","Latitude","Longitude","Year"))

test_labels_predropped_read = xr.open_dataset("/glade/work/acheung/Initial_RF_Datasets/test_labels_predropped.nc")
test_labels_predropped = test_labels_predropped_read.stack(z=("Month","Latitude","Longitude","Year"))

# For points that have no data, take closest point (< 300 km) or delete
trainunstacklabels = take_closest_point(train_labels_predropped,train_NaNlocs,train_stacked,vars_list)
testunstacklabels = take_closest_point(test_labels_predropped,test_NaNlocs,test_stacked,vars_list)

# Stack labels (obs) and drop NaN locations (resulting from no env data, usually over land)
trainstackedlabels = trainunstacklabels.stack(z=("Month","Latitude","Longitude","Year"))
train_labels = trainstackedlabels.drop_isel(z=train_NaNlocs)
teststackedlabels = testunstacklabels.stack(z=("Month","Latitude","Longitude","Year"))
test_labels = teststackedlabels.drop_isel(z=test_NaNlocs)

# Fit RF Model
clf = RandomForestClassifier()
clf.fit(train_env_data, train_labels.Genesis_Grids)
probs = clf.predict_proba(test_env_data)
genesisprobs = 1 - probs[:,0]
testprobs_formatted = xr.DataArray(genesisprobs,coords=test_labels.coords).unstack() # Genesis probability

# Unstack and formatted test labels (observed)
testlabelpoints = test_labels.Genesis_Grids.unstack()
trainlabelpoints = train_labels.Genesis_Grids.unstack()
# Save testlabelpoints (observed) and testprobs_formatted (prediction)
testlabelpoints.to_netcdf("/glade/work/acheung/Initial_RF_Datasets/test_label_points_obs.nc")
trainlabelpoints.to_netcdf("/glade/work/acheung/Initial_RF_Datasets/train_label_points_obs.nc")
testprobs_formatted.to_netcdf("/glade/work/acheung/Initial_RF_Datasets/probabilities_prediction.nc")