import netCDF4 as nc
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
from datetime import datetime

import os

# Directory containing all the NetCDF files
directory='/home/rosario/OXALA/environment/water/rain_pattern/data/ipma/mensal/'

# Specify the latitude and longitude of Monchique land
target_lat = 37.24
target_lon = -8.70

# Initialize empty lists to store data
all_time_data = []
all_precip_data = []


# Loop through all the NetCDF files in the directory
for filename in sorted(os.listdir(directory)):
    if filename.startswith("PRECIP_PT_mensal") and filename.endswith(".nc"):
        file_path = os.path.join(directory, filename)
        try:
            # Open the NetCDF file
            dataset = nc.Dataset(file_path)

            # Access the variables
            time_var = dataset.variables['time']
            lat_var = dataset.variables['lat']
            lon_var = dataset.variables['lon']
            precip_var = dataset.variables['var228']

            # Read data from the variables
            time_data = time_var[:]
            precip_data = precip_var[:]


            # Find the index corresponding to the target latitude and longitude
            # location index [25,5] - Monchique Area
            # Calculate the index based on the closest value to the target latitude and longitude
            lat_idx =  np.abs(lat_var[:] - target_lat).argmin()
            lon_idx =  np.abs(lon_var[:] - target_lon).argmin()
    
            # Close the NetCDF file
            dataset.close()  
            
            
            # Convert the time data to a more readable format ('YYYY-MM-DD')
            time_strings = [datetime.strptime(str(int(date)), '%Y%m%d').strftime('%Y-%m') for date in time_data]

            # Append data to the lists
            all_time_data.extend(time_strings)
            all_precip_data.extend(precip_data[:, lat_idx, lon_idx])

        except Exception as e:
            print(f"An error occurred while processing {filename}: {e}")


# Sort the time data
sorted_data = sorted(zip(all_time_data, all_precip_data), key=lambda x: x[0])
all_time_data, all_precip_data = zip(*sorted_data)    
        

# Create a plot of Montlhy Accumulates Precepitation
plt.figure(figsize=(16, 9))
plt.plot(all_time_data, all_precip_data, marker='o', linestyle='-', color='tab:blue', label='Accumulated Monthly Precipitation')
plt.xlabel('Date', fontsize=16)
plt.ylabel('Precipitation (mm)', fontsize=16)
plt.title('Monthly Precipitation at Latitude {target_lat}, Longitude {target_lon}', fontsize=18)
plt.xticks(rotation=80)
plt.tick_params(axis='both', labelsize=14)  # Adjust the fontsize as needed

# Set custom ticks (show every nth tick)
n = 12  # Adjust n to control the number of ticks shown
plt.xticks(np.arange(0, len(all_time_data), n), all_time_data[::n])

# Create custom legend entries for the blue points and orange vertical lines
blue_line = mlines.Line2D([], [], color='tab:blue', marker='o', linestyle='-', markersize=8, label='Precipitation Points', linewidth=2)
orange_line = mlines.Line2D([], [], color='tab:orange', linestyle='--', label='Yearly Marker', linewidth=2)

# Add the custom legend entries to the legend
plt.legend(handles=[blue_line, orange_line], fontsize=14)


# Highlight the yearly cycle with vertical lines
years = set(date.split('-')[0] for date in all_time_data)
for year in years:
    year_start = all_time_data.index(f"{year}-01")
    plt.axvline(x=year_start, color='tab:orange', linestyle='--', alpha=0.5, linewidth=2)
#    plt.text(year_start, max(all_precip_data), year, ha='center', va='bottom', rotation=90, color='gray', fontsize=9)

plt.grid(True)
plt.tight_layout()

plt.savefig(directory+'monchique_monthly_precipitation_1950_2003', format='png')

# Show the plot
plt.show()



#----------------------------------------------------------------------------



# Calculate accumulated rainfall per year
years = set(date.split('-')[0] for date in all_time_data)
accumulated_rain_per_year = {}
for year in years:
    year_indices = [i for i, date in enumerate(all_time_data) if date.startswith(year)]
    year_rainfall = sum(all_precip_data[i] for i in year_indices)
    accumulated_rain_per_year[year] = year_rainfall
    
# Calculate the average rainfall per year
average_rainfall = np.mean(list(accumulated_rain_per_year.values()))

# Create a list of (year, accumulated precipitation) tuples and sort it by year
yearly_data = sorted(list(accumulated_rain_per_year.items()), key=lambda x: int(x[0]))
# Extract the sorted years and accumulated rainfall values
years_list, rainfall_list = zip(*yearly_data)
average_accumulated_rainfall = np.mean(rainfall_list)


# Find the year(s) with maximum and minimum accumulated precipitation
max_rainfall_year = years_list[np.argmax(rainfall_list)]
min_rainfall_year = years_list[np.argmin(rainfall_list)]


plt.figure(figsize=(10, 6))
plt.bar(years_list, rainfall_list, color='tab:blue', alpha=0.7, label='Yearly Accumulated Precipitation')
plt.xlabel('Year', fontsize=9)
plt.ylabel('Accumulated Precipitation (mm)', fontsize=10)
plt.title(f'Yearly Accumulated Precipitation at Latitude {target_lat}, Longitude {target_lon}', fontsize=16)
plt.xticks(rotation=80)



# Highlight the year with maximum accumulated precipitation
plt.axvline(x=max_rainfall_year, color='green', linestyle='--', linewidth=2, alpha=0.7,label=f'Max Precipitation Year {max_rainfall_year}')

# Highlight the year with minimum accumulated precipitation
plt.axvline(x=min_rainfall_year, color='tab:red', linestyle='--', linewidth=2, alpha=0.7,label=f'Min Precipitation Year {min_rainfall_year}')

# Add a horizontal line for the average
plt.axhline(y=average_accumulated_rainfall, color='tab:orange', linestyle='-', alpha=0.7, linewidth=2, label='Average Yearly Precipitation')

plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig(directory+'monchique_yearly_precipitation_1950_2003', format='png')

# Show the second plot
plt.show()


#-------------------------------------


# Calculate the histogram of monthly precipitation values
hist, bin_edges = np.histogram(all_precip_data, bins=30)

# Create a figure with two subplots
fig, (ax0, ax1) = plt.subplots(nrows=1, ncols=2, figsize=(16, 9), gridspec_kw={'width_ratios': [3, 1]}, sharey=True)

# Plot monthly precipitation data on the left subplot
ax0.plot(all_time_data, all_precip_data, marker='o', linestyle='-', color='tab:blue', label='Accumulated Monthly Precipitation')
ax0.set_xlabel('Date', fontsize=16)
ax0.set_ylabel('Precipitation (mm)', fontsize=16)
ax0.set_title(f'Monthly Precipitation at Latitude {target_lat}, Longitude {target_lon}', fontsize=18)
ax0.tick_params(axis='both', labelsize=14)  # Adjust the fontsize as needed

# Add a light grey horizontal grid for the precipitation values on the left subplot
ax0.grid(axis='y', linestyle='--', alpha=1)

# Set custom ticks (show every nth tick)
n = 12  # Adjust n to control the number of ticks shown
ax0.set_xticks(np.arange(0, len(all_time_data), n))
ax0.set_xticklabels(all_time_data[::n], rotation=80)

# Create custom legend entries for the blue points and orange vertical lines
blue_line = mlines.Line2D([], [], color='tab:blue', marker='o', linestyle='-', markersize=8, label='Precipitation Points', linewidth=2)
orange_line = mlines.Line2D([], [], color='tab:orange', linestyle='--', label='Yearly Marker', linewidth=2)
ax0.legend(handles=[blue_line, orange_line], fontsize=14)

# Highlight the yearly cycle with vertical lines on the left subplot
years = set(date.split('-')[0] for date in all_time_data)
for year in years:
    year_start = all_time_data.index(f"{year}-01")
    ax0.axvline(x=year_start, color='tab:orange', linestyle='--', alpha=0.5, linewidth=2)

# Plot the histogram on the right subplot
ax1.hist(all_precip_data, bins=30, orientation='horizontal', color='tab:blue', alpha=0.6)
ax1.set_xlabel('Frequency', fontsize=16)
ax1.set_title('Precipitation Histogram', fontsize=18)
ax1.tick_params(axis='both', labelsize=14)

# Remove the y-label of the histogram
ax1.set_yticklabels([])

# Add a light grey horizontal grid for the precipitation values on the right subplot
ax1.grid(axis='y', linestyle='--', alpha=1)
ax1.grid(axis='x', linestyle='--', alpha=0.8)

# Adjust the layout
plt.tight_layout()

# Save the figure
plt.savefig(directory + 'monchique_monthly_precipitation_with_histogram_1950_2003.png', format='png')

# Show the plot
plt.show()


#-----------------------------------------------------


# Calculate accumulated rainfall per year
years = set(date.split('-')[0] for date in all_time_data)
accumulated_rain_per_year = {}
for year in years:
    year_indices = [i for i, date in enumerate(all_time_data) if date.startswith(year)]
    year_rainfall = sum(all_precip_data[i] for i in year_indices)
    accumulated_rain_per_year[year] = year_rainfall

# Calculate the average rainfall per year
average_rainfall = np.mean(list(accumulated_rain_per_year.values()))

# Create a list of (year, accumulated precipitation) tuples and sort it by year
yearly_data = sorted(list(accumulated_rain_per_year.items()), key=lambda x: int(x[0]))
# Extract the sorted years and accumulated rainfall values
years_list, rainfall_list = zip(*yearly_data)
average_accumulated_rainfall = np.mean(rainfall_list)

# Find the year(s) with maximum and minimum accumulated precipitation
max_rainfall_year = years_list[np.argmax(rainfall_list)]
min_rainfall_year = years_list[np.argmin(rainfall_list)]

# Create a figure with two subplots
fig, (ax0, ax1) = plt.subplots(nrows=1, ncols=2, figsize=(16, 9), gridspec_kw={'width_ratios': [3, 1]}, sharey=True)

# Plot yearly accumulated precipitation data on the left subplot
ax0.bar(years_list, rainfall_list, color='tab:blue', alpha=0.7, label='Yearly Accumulated Precipitation')
ax0.set_xlabel('Year', fontsize=9)
ax0.set_ylabel('Accumulated Precipitation (mm)', fontsize=16)
ax0.set_title(f'Yearly Accumulated Precipitation at Latitude {target_lat}, Longitude {target_lon}', fontsize=18)
ax0.tick_params(axis='both', labelsize=14)  # Adjust the fontsize as needed
ax0.set_xticklabels(years_list, rotation=80)

# # Highlight the year with maximum accumulated precipitation
ax0.axvline(x=max_rainfall_year, color='green', linestyle='--', linewidth=2, alpha=0.7, 
            label=f'Max Precipitation Year {max_rainfall_year}')

# # Highlight the year with minimum accumulated precipitation
ax0.axvline(x=min_rainfall_year, color='tab:red', linestyle='--', linewidth=2, alpha=0.7,
             label=f'Min Precipitation Year {min_rainfall_year}')

# Add a light grey horizontal grid for the precipitation values on the y-axis
ax0.yaxis.grid(color='lightgrey', linestyle='--', alpha=1)

# Add a light grey vertical grid
ax0.xaxis.grid(color='lightgrey', linestyle='--', alpha=0.5)

ax0.legend()

# Plot the histogram on the right subplot
ax1.hist(rainfall_list, bins=30, orientation='horizontal', color='tab:blue', alpha=0.7)
ax1.set_xlabel('Frequency', fontsize=16)
ax1.set_title('Yearly Precipitation Histogram', fontsize=18)
ax1.tick_params(axis='both', labelsize=14)

# Remove the y-label of the histogram
#ax1.set_yticklabels([])

# Add a light grey horizontal grid for the precipitation values on the right subplot
ax1.grid(axis='y', linestyle='--', alpha=1)
ax1.grid(axis='x', linestyle='--', alpha=0.8)

# Adjust the layout
plt.tight_layout()

# Save the figure
plt.savefig(directory + 'monchique_yearly_precipitation_with_histogram_1950_2003.png', format='png')

# Show the plot
plt.show()