def date_range_list_creator(years,day_resolution): # THIS SCRIPT NEEDS TO BE MODIFIED IF YEARS ARE NOT CONSECUTIVE!!!

    # We want to process genesis grid locations for the inputted temporal resolution within the inputted years
    import datetime as dt
    import copy

    first_year = years[0]
    end_year = years[-1]


    first_month_dt = dt.datetime(first_year,1,1)
    last_month_dt = dt.datetime(end_year,12,31) # we are doing yearly (so this is the same year)

    date_range_list = []
    current_dt = copy.deepcopy(first_month_dt)
    date_range_list.append(current_dt)

    # Create a list of datetimes from start to last full year

    while current_dt.year <= end_year: 
        current_dt = current_dt + dt.timedelta(days=day_resolution)
        if current_dt.year <= end_year:    
            date_range_list.append(current_dt)
        if current_dt.year > end_year: # If the last few days are less than seven days, take data only until the end of the year to prevent spillover
            date_range_list.append(current_dt - dt.timedelta(days=current_dt.day-1))
            
    return date_range_list


def genesis_grid_creator(basin_dataset,date_range_list,day_resolution,years,min_wspd):

    import datetime as dt
    import xarray as xr
    import pandas as pd
    import numpy as np

    # Grab data for a desired range of seasons
    szn_DF = basin_dataset.get_season(years[0]).to_dataframe() # Get information of year

    for year in years[1:]:
        szn_DF = pd.concat([szn_DF,basin_dataset.get_season(year).to_dataframe()]) # Get information of year

    szn_DF_starts = szn_DF.set_index(['start_time'])
    szn_DF_starts = szn_DF_starts.sort_index()


    total_data_arr_list = []

    delta_degs = 0.25 # Size of boxes in degrees
    lon_ranges = [-100,0] # Lon range to count (in the last value, add 10 to your desired value)
    lat_ranges = [0,60] # Lat range to count (in the last value, add 10 to your desired value)
    latgrid = np.arange(lat_ranges[0],lat_ranges[1]+0.0000001,delta_degs)
    longrid = np.arange(lon_ranges[0],lon_ranges[1]+0.0000001,delta_degs)

    for date_range_desired in range(len(date_range_list)): # Loop of current daterange

        start_time = date_range_list[date_range_desired]
        end_time = start_time + dt.timedelta(days=day_resolution)


        # Set Minimum Wind Speed Requirement (THIS ONLY FILTERS WEAK STORMS!) Still need to find first time of a certain intensity!
        below_reqs_inds = np.where(szn_DF_starts['vmax'] < min_wspd)
        szn_DF = szn_DF_starts.drop(below_reqs_inds[0])

        # Sort genesis events by month
        gens_in_range = szn_DF_starts.loc[str(start_time):str(end_time)]

        # Record the genesis lat and lons
        start_lats = gens_in_range['start_lat']
        start_lons = gens_in_range['start_lon']
        H, xedges, yedges = np.histogram2d(start_lats, start_lons, bins=(latgrid, longrid))
        total_data_arr_list.append(H)    

    labels = xr.DataArray(total_data_arr_list,coords=[("Start_Date",date_range_list),("Latitude",latgrid[0:-1].astype(float)),
                                                      ("Longitude",longrid[0:-1].astype(float))])
    return labels