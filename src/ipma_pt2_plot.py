import argparse
import netCDF4 as nc
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
from datetime import datetime

import os

def read_inputs(directory,target_lat,target_lon):
    # Latitude and longitude of Herdade da Bravura
    #target_lat = 37.24    # location index [25,5] - Monchique Area
    #target_lon = -8.70
    
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
    return sorted_data,all_time_data, all_precip_data



def plot_monthly_precip_histogram(all_time_data,all_precip_data,target_lat,target_lon):
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
    #ax1.set_yticklabels([])
    
    # Add a light grey horizontal grid for the precipitation values on the right subplot
    ax1.grid(axis='y', linestyle='--', alpha=1)
    ax1.grid(axis='x', linestyle='--', alpha=0.8)
    
    # Adjust the layout
    plt.tight_layout()
    
    # Save the figure
    plt.savefig('bravura_monthly_precipitation_with_histogram_1950_2003.png', format='png')
    
    # Show the plot
    plt.show()
    
    
def plot_monthly_precip(sorted_data, all_time_data, target_lat,target_lon):
    # Create a dictionary to map months to their respective season colors
    month_colors = {
        1: ('January', '#0000FF'),    # January - Winter (Dark Blue)
        2: ('February', '#3399FF'),   # February - Winter (Light Blue)
        3: ('March', '#228B22'),      # March - Spring (Forest Green)
        4: ('April', '#32CD32'),      # April - Spring (Lime Green)
        5: ('May', '#3CB371'),        # May - Spring (Medium Sea Green)
        6: ('June', '#FF6347'),       # June - Summer (Tomato)
        7: ('July', '#FF4500'),       # July - Summer (Orange Red)
        8: ('August', '#FF0000'),     # August - Summer (Red)
        9: ('September', '#FFA500'),  # September - Autumn (Orange)
        10: ('October', '#D2691E'),   # October - Autumn (Chocolate)
        11: ('November', '#8B4513'),  # November - Autumn (Saddle Brown)
        12: ('December', '#000080')   # December - Winter (Navy)
    }
    
    # Create a figure for the line plot
    plt.figure(figsize=(12, 6))
       
    # Extract years from time data
    years = list(set([int(date.split('-')[0]) for date in all_time_data]))
    
    # Split the data into batches of 12 months each
    batch_size = 12
    year_batches = [sorted_data[i:i+batch_size] for i in range(0, len(sorted_data), batch_size)]
    
    for y in range(0,len(year_batches)):
        # Plot each month's accumulated precipitation
        bottom=0
        for m in range(0, 12):
            precip_value = year_batches[y][m][1]
            year=int(year_batches[y][m][0].split('-')[0])
            month_name,color=month_colors[m+1]
            plt.bar(year, precip_value, color=color,bottom=bottom)
            bottom += precip_value
        
    
    plt.xlabel('Year', fontsize=14)
    plt.ylabel('Precipitation (mm)', fontsize=14)
    plt.title(f' Yearly Precipitation at Latitude {target_lat}, Longitude {target_lon} monthly contribution', fontsize=16)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Configure x-axis ticks
    plt.xticks(years,rotation=80)
    plt.grid(axis='both', linestyle='--', alpha=0.5)
    
    # Create a legend outside the loop
    legend_labels = [plt.Line2D([0], [0], color=month_colors[m][1], lw=4, label=month_colors[m][0]) for m in range(1,13)]
    plt.legend(handles=legend_labels, fontsize=10, title="Months", title_fontsize=12, loc='upper left')
    
    plt.tight_layout()
    
    # Save the figure
    plt.savefig('bravura_yearly_precipitation_per_month_1950_2003.png', format='png')
    
    plt.show()    
    
def plot_yearly_precip(all_time_data, all_precip_data, target_lat,target_lon):
    # Calculate accumulated rainfall per year
    years = set(date.split('-')[0] for date in all_time_data)
    accumulated_rain_per_year = {}
    for year in years:
        year_indices = [i for i, date in enumerate(all_time_data) if date.startswith(year)]
        year_rainfall = sum(all_precip_data[i] for i in year_indices)
        accumulated_rain_per_year[year] = year_rainfall
    
    # Create a list of (year, accumulated precipitation) tuples and sort it by year
    yearly_data = sorted(list(accumulated_rain_per_year.items()), key=lambda x: int(x[0]))
    # Extract the sorted years and accumulated rainfall values
    years_list, rainfall_list = zip(*yearly_data)
    
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
    
    ax0.yaxis.grid(color='lightgrey', linestyle='--', alpha=1)
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
    plt.savefig('bravura_yearly_precipitation_with_histogram_1950_2003.png', format='png')
    
    # Show the plot
    plt.show()


def main(target_lat, target_lon, data_directory):
    # Get the absolute path to the data directory
    directory = os.path.join(os.path.dirname(__file__), data_directory)

    sorted_data, all_time_data, all_precip_data = read_inputs(directory,target_lat,target_lon)


    plot_monthly_precip_histogram(all_time_data, all_precip_data,target_lat,target_lon)
    plot_monthly_precip(sorted_data, all_time_data, target_lat,target_lon)
    plot_yearly_precip(all_time_data, all_precip_data, target_lat,target_lon)
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process precipitation data.")
    parser.add_argument("--lat", type=float, required=True, help="Latitude")
    parser.add_argument("--lon", type=float, required=True, help="Longitude")
    parser.add_argument("--data-directory", type=str, required=True, help="Relative path to data directory")
    args = parser.parse_args()

    main(args.lat, args.lon, args.data_directory)
    
    
    
    

