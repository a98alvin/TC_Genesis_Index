# Compile a specific environmental variable from all times
def data_compiler(vardesired):
    import os
    import re
    import numpy as np
    from scipy.io import loadmat
    import xarray as xr

    path = "/glade/work/acheung/TC_Genesis/" + vardesired
    dir_list = os.listdir(path) # List of filenames
    dir_list.sort()
    Varcompiled = []
    YearList = []
    for dir_list_now in dir_list:
        mylist = [dir_list_now] # init the list
        for l in mylist:
            match = re.match(r'.*([1-3][0-9]{3})', l)
        year = match[0][-4:]
        annots = loadmat('/glade/work/acheung/TC_Genesis/' + vardesired+'/'+dir_list_now)
        if vardesired == 'PI_ERA5':
            variablekey = 'VmaxI'
        else:
            variablekey = list(annots.keys())[-1]
        Var = np.asarray(annots[variablekey])
        Varcompiled.append(Var)
        YearList.append(year)
    Varcompiled = np.asarray(Varcompiled)
    lons = np.asarray(annots['Xg'])[:,0]
    lats = np.asarray(annots['Yg'])[:,0]
    arr = xr.DataArray(Varcompiled,coords=[("Year",range(1950,2021)),("Latitude",lats),("Longitude",lons),("Month",range(1,13))],attrs=dict(
        description=vardesired))
    
    return Varcompiled, YearList,lons,lats,arr

# Find Genesis Locations by Year and Month
def month_genesis_locs(year_desired,month_desired,basin_dataset,min_wspd):
    from calendar import monthrange
    from datetime import date as dt
    import numpy as np
    year_desired = int(year_desired)
    month_desired = int(month_desired)
    szn_DF = basin_dataset.get_season(year_desired).to_dataframe() # Get information of year
  
    # Set Minimum Wind Speed Requirement (THIS ONLY FILTERS WEAK STORMS!) Still need to find first time of a certain intensity!
    below_reqs_inds = np.where(szn_DF['vmax'] < min_wspd)
    szn_DF = szn_DF.drop(below_reqs_inds[0])
    
    # Set time as index
    szn_DF_starts = szn_DF.set_index(['start_time'])

    days_in_month = monthrange(year_desired, month_desired)[1] # Identify the number of days in a month
    
    # Sort genesis events by month
    gen_by_month = szn_DF_starts.loc[str(dt(year=year_desired,
                                            month=month_desired,day=1)):str(dt(year=year_desired,month=month_desired,day=days_in_month))]

    # Record the genesis lat and lons
    start_lats = gen_by_month['start_lat']
    start_lons = gen_by_month['start_lon']
    return start_lons,start_lats

# Grid Counter
def grid_counter(delta_degs,lon_ranges,lat_ranges,start_lons,start_lats):
    import numpy as np
    
    latgrid = np.arange(lat_ranges[0],lat_ranges[1],delta_degs)
    longrid = np.arange(lon_ranges[0],lon_ranges[1],delta_degs)

    total_data_arr = []
    for latnow in latgrid:
        lat_data_arr = []
        for lonnow in longrid:
            latinds = np.where((start_lats >= latnow) & (start_lats < (latnow + delta_degs)))[0]
            loninds = np.where((start_lons >= lonnow) & (start_lons < (lonnow + delta_degs)))[0]
            genesis_in_box_inds = np.intersect1d(latinds,loninds)
            gen_number = len(genesis_in_box_inds)
            lat_data_arr.append(gen_number)
        total_data_arr.append(lat_data_arr)

    total_data_arr = np.asarray(total_data_arr)
    return total_data_arr,longrid,latgrid

def environmental_select_stack(month_range,year_range,Latitude,Longitude,arr):
    import numpy as np
    arr_select = arr.sel(Latitude=Latitude,Longitude=Longitude,Year=year_range,Month=month_range)
    stacked = arr_select.stack(z=("Month","Latitude","Longitude","Year"))

    # Find all places where any of the variables have a NaN
    allnanlocs = []
    for CX in range(0,np.shape(stacked)[0]):
        currentNaNlocs = np.where(stacked[CX].isnull())[0]
        allnanlocs.append(currentNaNlocs)
    NaNlocs = np.unique(np.concatenate(allnanlocs,axis=0))
    
    return stacked,NaNlocs

def create_genesis_grid_labels(month_range,year_range,vmin,basin_dataset):
    from useful_functions import month_genesis_locs
    from useful_functions import grid_counter
    import xarray as xr
    
    all_months_total_data_arr = []
    for month_desired in month_range: # Loop of current month (Sorted by month)
            single_year_data_arr = []
            for year_now in year_range: # Loop of current year 
                start_lons,start_lats = month_genesis_locs(year_now,month_desired,basin_dataset,vmin)

                # Grid Counter
                delta_degs = 2 # Size of boxes in degrees
                lon_ranges = [-100,0] # Lon range to count (in the last value, add 10 to your desired value)
                lat_ranges = [0,80] # Lat range to count (in the last value, add 10 to your desired value)
                total_data_arr,longrid,latgrid = grid_counter(delta_degs,lon_ranges,lat_ranges,start_lons,start_lats) # Call grid_counter function

                longridnew = longrid + 360 # WARNING: This only works for Atlantic Basin (need to modify if changing domain)
                single_year_data_arr.append(total_data_arr)

              #  print('Current Month: ' + str(month_desired) + ' Current Year: ' + str(year_now))

            all_months_total_data_arr.append(single_year_data_arr)

    labels = xr.DataArray(all_months_total_data_arr,coords=[("Month",month_range),("Year",year_range),("Latitude",latgrid.astype(float)),("Longitude",longridnew.astype(float))])
    labels_stack = labels.stack(z=("Month","Latitude","Longitude","Year"))
    
    return labels_stack

def take_closest_point(labels_predropped,NaNlocs,envstack,vars_list):

    import pandas as pd
    import numpy as np
    from distance import pointdist_calc

    
    labels_tbd = labels_predropped.__xarray_dataarray_variable__[NaNlocs]
    badgenlocs = np.where(labels_tbd > 0)[0]
    unstacklabels = labels_predropped.unstack()

    counter = 0
    # Find distance from would've been dropped label
    for baditerations in range(0,len(badgenlocs)):
        current_tbd_label = labels_tbd[badgenlocs[baditerations]]
        current_tbd_lon = current_tbd_label.coords['Longitude']
        current_tbd_lat = current_tbd_label.coords['Latitude']

        # Find location and distance of closest non NaN data point for all vars
        allcurrentbooleans = []
        for variablecheck in range(0,len(vars_list)):

            currentdata_to_rect = envstack.sel(Month=float(current_tbd_label.coords['Month']),Year = float(current_tbd_label.coords['Year']),
                             Variable=vars_list[variablecheck])

            # Find distances of every point in data to the bad label location
            currentdistancesarr = []
            for indivpoint in range(0,len(currentdata_to_rect)):
                current_data_lat = float(currentdata_to_rect[indivpoint].coords['Latitude'])
                current_data_lon = float(currentdata_to_rect[indivpoint].coords['Longitude'])
                distance_to_bad = pointdist_calc(current_data_lat,current_data_lon,current_tbd_lat,current_tbd_lon)
                currentdistancesarr.append(distance_to_bad)

            currentboolean = currentdata_to_rect.isnull()
            allcurrentbooleans.append(list(np.asarray(currentboolean)))

        allboospd = pd.DataFrame(allcurrentbooleans).transpose()
        allboospd.columns=vars_list
        distspd = pd.DataFrame(currentdistancesarr,columns=['Distance'])
        allvarswithdistpd = pd.concat([allboospd,distspd],axis=1)
        goodplaces = allvarswithdistpd.loc[(allvarswithdistpd[vars_list[0]] == False) & (allvarswithdistpd[vars_list[1]] == False) & (allvarswithdistpd[vars_list[2]] == False) & (allvarswithdistpd[vars_list[3]] == False)]
        locusedpre = np.where(goodplaces['Distance'] == np.min(goodplaces['Distance']))[0][0]
        locused = goodplaces.iloc[locusedpre].name

        print(np.min(goodplaces['Distance']) < 300)
        if np.min(goodplaces['Distance']) < 300: # change closest point to yes
            locinfo = labels_predropped.__xarray_dataarray_variable__.sel(Month=float(current_tbd_label.coords['Month']),Year = float(current_tbd_label.coords['Year']))[locused]
            monthinfo = float(locinfo.Month)
            yearinfo = float(locinfo.Year)
            latinfo = float(locinfo.Latitude)
            loninfo = float(locinfo.Longitude)    
            unstacklabels.__xarray_dataarray_variable__.loc[monthinfo,latinfo,loninfo,yearinfo] = unstacklabels.__xarray_dataarray_variable__.loc[monthinfo,latinfo,loninfo,yearinfo] + float(current_tbd_label)
            counter = counter + 1
            print('action performed #' + str(counter))
    return unstacklabels