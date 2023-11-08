import argparse
import netCDF4 as nc
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib.dates as mdates
import seaborn as sns
from scipy.stats import norm

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


    
def plot_yearly_precip(sorted_data, target_lat, target_lon):
    df_precip = pd.DataFrame(sorted_data, columns=['Date', 'Precipitation'])
    # Convert the 'Date' column to datetime format (only the year part will be significant)
    df_precip['Year'] = pd.to_datetime(df_precip['Date'], format='%Y-%m')
    
    df_precip['Year'] = df_precip['Year'].dt.year
    accumulated_rain_year = df_precip.groupby('Year')['Precipitation'].sum().reset_index()

    # Find the year(s) with maximum and minimum accumulated precipitation
    max_rainfall_year = accumulated_rain_year.loc[accumulated_rain_year['Precipitation'].idxmax(),'Year']
    min_rainfall_year = accumulated_rain_year.loc[accumulated_rain_year['Precipitation'].idxmin(),'Year']
    
      
    # Seaborn color palette for the histogram
    palette = sns.color_palette("husl", n_colors=8)
    sns.set_palette(palette)   
    
    # Create a figure with two subplots
    fig, (ax0, ax1) = plt.subplots(nrows=1, ncols=2, figsize=(16, 9), gridspec_kw={'width_ratios': [3, 1]}, sharey=True)
    
    # Plot yearly accumulated precipitation data on the left subplot
    ax0.bar(accumulated_rain_year['Year'], accumulated_rain_year['Precipitation'], color=palette[5], alpha=0.7, label='Yearly Accumulated Precipitation')
    ax0.set_xlabel('Year', fontsize=16)
    ax0.set_ylabel('Accumulated Precipitation (mm)', fontsize=16)
    ax0.set_title(f'Yearly Accumulated Precipitation at Bravura ({target_lat},{target_lon})', fontsize=18)

    #ax0.set_xticklabels(accumulated_rain_year['Year'], rotation=80)
  
    ax0.tick_params(axis='both', labelsize=14)  # Adjust the fontsize as needed

    # Enable grid for x-axis with the specified locator as reference for gridlines
    ax0.grid(True, which='major', axis='both', linestyle='--', color='lightgrey', alpha=0.7)   

    # # Highlight the year with maximum accumulated precipitation
    ax0.axvline(x=max_rainfall_year, color=palette[4], linestyle='--', linewidth=2, alpha=0.7, 
                label=f'Max Precipitation Year {max_rainfall_year}')   
    # # Highlight the year with minimum accumulated precipitation
    ax0.axvline(x=min_rainfall_year, color=palette[0],linestyle='--', linewidth=2, alpha=0.7,
                 label=f'Min Precipitation Year {min_rainfall_year}')
    
    ax0.yaxis.grid(color='lightgrey', linestyle='--', alpha=1)
    ax0.xaxis.grid(color='lightgrey', linestyle='--', alpha=0.5)
    
    mean_precipitation = accumulated_rain_year['Precipitation'].mean()
    median_precipitation = accumulated_rain_year['Precipitation'].median()
    max_precipitation = accumulated_rain_year['Precipitation'].max()
    min_precipitation = accumulated_rain_year['Precipitation'].min()
    std_deviation_precipitation = accumulated_rain_year['Precipitation'].std()
    # Calculate variance
    variance_precipitation = accumulated_rain_year['Precipitation'].var()
    # Calculate percentiles (25th, 50th, and 75th percentiles)
    percentiles = np.percentile(accumulated_rain_year['Precipitation'], [25, 50, 75])

    
    # Print specific statistics
    print(f"Mean Precipitation: {mean_precipitation}")
    print(f"Median Precipitation: {median_precipitation}")
    print(f"Max Precipitation: {max_precipitation}")
    print(f"Min Precipitation: {min_precipitation}")
    print(f"Variance of Precipitation: {variance_precipitation}")
    print(f"25th Percentile: {percentiles[0]}")
    print(f"50th Percentile (Median): {percentiles[1]}")
    print(f"75th Percentile: {percentiles[2]}")
    print(f"Standard Deviation of Precipitation: {std_deviation_precipitation}")

    
    # Plot the histogram on the right subplot
    hist, bins, _ = ax1.hist(accumulated_rain_year['Precipitation'], bins=30, orientation='horizontal', color=palette[4], alpha=0.7, label='Precipitation Probability Density')
    ax1.set_xlabel('Probability Density', fontsize=16)
#    ax1.set_title('Precipitation Volume Freq.', fontsize=18)
    ax1.tick_params(axis='both', labelsize=14)
    
    
    # Calculate mean and standard deviation for Gaussian distribution
    mu, std = norm.fit(accumulated_rain_year['Precipitation'])
    # Calculate the Gaussian distribution centered on the mean precipitation value
    x = np.linspace(mu - 3 * std, mu + 3 * std, 100)  # Adjust the range as needed
    p = norm.pdf(x, mu, std)
    
    # Normalize the Gaussian distribution so that its maximum height is 7
    max_height = 7
    scaling_factor = max_height / np.max(p)
    p *= scaling_factor
    
    
    # Plot the Gaussian distribution on the right subplot
    ax1.plot(p, x, linewidth=1, color=palette[5], alpha=0.7, label='Precip. Normal Distribution')
    
    # add legends
    ax0.legend()
    ax1.legend()
    
    # Add a light grey horizontal grid for the precipitation values on the right subplot
    ax1.grid(axis='y', linestyle='--', alpha=1)
    ax1.grid(axis='x', linestyle='--', alpha=0.8)
    
    # Adjust the layout
    plt.tight_layout()
    
    # Save the figure
    plt.savefig('bravura_yearly_precipitation_with_histogram_1950_2003.png', format='png')
    
    # Show the plot
    plt.show()


def plot_waterlevel_yearly(all_time_data, all_precip_data, target_lat,target_lon):

    
    # Define the CSV file path
    csv_file = '/home/rosario/AdBravura/environment/water/combined/data_water_level/watershed_yearly.csv'
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file)
    # Convert the 'date' column to datetime format (if it's not already)
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m')
    # Sort the DataFrame by date
    df.sort_values(by='date', inplace=True)
    
    
    # load Seaborn color palette 
    palette = sns.color_palette("husl", n_colors=16)
    sns.set_palette(palette)
    # Define a list of colors to alternate between
    colors = [palette[6],palette[3]]
    
    # Create a line plot
    plt.figure(figsize=(13, 5))
    
    # Create a line plot going through the points
    plt.plot(
        df['date'],
        df['qualitative_water_level'],
        linestyle='-',
        color=palette[6],
        alpha=0.8,
        label='Line through Points'
    )
    
    # Iterate through the rows and plot data points with alternating colors
    for i, row in enumerate(df.iterrows()):
        plt.plot(
            row[1]['date'],
            row[1]['qualitative_water_level'],
            marker='o',
            linestyle='-',
            color=colors[i % 2],  # Alternate between the two colors
        )  
    
    
    # Customize the plot
    plt.title('Qualitative Water Level Over Time', size=20)
    plt.xlabel('Date', size=16)
    plt.ylabel('Qualitative Water Level', size=16)
    plt.xticks(rotation=45)
    
    # Customize the vertical axis labels
    y_values = [1, 2, 3, 4]
    y_labels = ["Ext.Low", "Low", "OK", "Full"]
    plt.yticks(y_values, y_labels)
    
    # Set x-axis ticks every 2 years (adjust as needed)
    x_ticks = pd.date_range(start=df['date'].min(), end=df['date'].max(), freq='2Y')
    plt.xticks(x_ticks, [x.strftime('%Y') for x in x_ticks])
    
    # Add vertical grid lines
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Create proxy artists for the legend
    legend_handles = [
        mlines.Line2D([], [], color=colors[1], marker='o', markersize=5, label='Autumn'),
        mlines.Line2D([], [], color=colors[0], marker='o', markersize=5, label='Spring')
    ]
    
    # Show the legend in the top-right corner
    plt.legend(handles=legend_handles, loc='upper right', title="Legend")
    
    # Save the plot to an image file (e.g., PNG)
    plt.savefig('water_level_plot.png')
    
    # Show the plot or save it to a file
    plt.tight_layout()
    plt.show()



def plot_combined_waterlevel_and_precip(sorted_data, target_lat, target_lon):
    
    # read input to dataframe
    df_precip = pd.DataFrame(sorted_data, columns=['Date', 'Precipitation'])
    # Convert the 'Date' column to datetime format (only the year part will be significant)
    df_precip['Year'] = pd.to_datetime(df_precip['Date'], format='%Y-%m')    
    df_precip['Year'] = df_precip['Year'].dt.year
    accumulated_rain_year = df_precip.groupby('Year')['Precipitation'].sum().reset_index()
    # Convert the 'Year' column back to a datetime format, setting all dates to the half of the year
    accumulated_rain_year['Year'] = pd.to_datetime(accumulated_rain_year['Year'].astype(str)) #+ pd.DateOffset(months=6)
    
    # Find the year(s) with maximum and minimum accumulated precipitation
    max_rainfall_year = accumulated_rain_year.loc[accumulated_rain_year['Precipitation'].idxmax(),'Year']
    min_rainfall_year = accumulated_rain_year.loc[accumulated_rain_year['Precipitation'].idxmin(),'Year']
    

    # Define the CSV file path for water level
    csv_file = '/home/rosario/AdBravura/environment/water/combined/data_water_level/watershed_yearly.csv'
    # Read the CSV file into a pandas DataFrame
    df_waterlevel = pd.read_csv(csv_file)
    df_waterlevel['date'] = pd.to_datetime(df_waterlevel['date'], format='%Y-%m')
    # Sort the DataFrame by date
    df_waterlevel.sort_values(by='date', inplace=True)

       
    # create figure
    fig, ax_precip = plt.subplots(figsize=(18, 8))
    # Duplicate x-axis
    ax_water = ax_precip.twinx()     
   
    # Set title
    ax_water.set_title('Accumulated Yearly Precipitation vs Qualitative Water Level', fontsize=16) 
   
    # load Seaborn color palette 
    palette = sns.color_palette("husl", n_colors=15)
    sns.set_palette(palette)

    # Plot the water level on a secondary y-axis.
    color_water=palette[7]
    ax_water.plot(df_waterlevel['date'], df_waterlevel['qualitative_water_level'], linestyle='-', linewidth=2, color=color_water, marker='o', alpha=0.5, label='Qualitative Water Level')

    # Now fill beneath the water level plot.
    ax_water.fill_between(df_waterlevel['date'], df_waterlevel['qualitative_water_level'], alpha=0.2, color=color_water)
    
    # Configure axis
    ax_water.set_ylim([0.5, 4.5])  # Assuming the water level is between 0 and 4
    # Customize the vertical axis labels
    y_values = [1, 2, 3, 4]
    y_labels = ["Ext.Low", "Low", "OK", "Full"]    
    plt.yticks(y_values, y_labels)    
    ax_water.tick_params(axis='y')
    ax_water.set_ylabel('Relative Water Level', fontsize=14)


    # define bins edges
    min_year = accumulated_rain_year['Year'].min()
    max_year = accumulated_rain_year['Year'].max()  + pd.DateOffset(years=1)
    date_bins = pd.date_range(start=min_year, end=max_year, freq='YS')
    
    # Plot Precipitation histogram.
    color_precip=palette[9]
    n, bins, patches = ax_precip.hist(accumulated_rain_year['Year'], bins=date_bins,
                                       weights=accumulated_rain_year['Precipitation'], alpha=0.7, rwidth=1,
                                       color=color_precip, label='Yearly Accumulated Precipitation', align='mid')

    # Set axis labels
    ax_precip.set_xlabel('Year', fontsize=10)
    ax_precip.set_ylabel('Accumulated Precipitation (mm)', fontsize=14)    
    ax_precip.set_ylim([0, 1300])
    


     # Add vertical lines at specific years (1950 and 1988)
    # ax_water.axvline(x=pd.to_datetime('1950-01-01'), color='red', linestyle='--', label='Year 1950')
    # ax_water.axvline(x=pd.to_datetime('1955-01-01'), color='blue', linestyle='--', label='Year 1955')
    # ax_water.axvline(x=pd.to_datetime('1960-01-01'), color='red', linestyle='--', label='Year 1950')
    # ax_water.axvline(x=pd.to_datetime('1965-01-01'), color='blue', linestyle='--', label='Year 1955')
    # ax_water.axvline(x=pd.to_datetime('1965-01-01'), color='red', linestyle='--', label='Year 1950')
    # ax_water.axvline(x=pd.to_datetime('1970-01-01'), color='blue', linestyle='--', label='Year 1955')
                    
    # ax_water.axvline(x=pd.to_datetime('1975-01-01'), color='red', linestyle='--', label='Year 1950')
    # ax_water.axvline(x=pd.to_datetime('1980-01-01'), color='blue', linestyle='--', label='Year 1955')
        
   
    # Combine the date ranges from both DataFrames and extract unique dates
    combined_dates = pd.concat([accumulated_rain_year['Year'].dt.year, df_waterlevel['date'].dt.year], ignore_index=True).unique()

    # Create a date range for ticks every 5 years from the minimum to maximum year
    start_year = min(combined_dates) 
    end_year = max(combined_dates)    
    # Create the range of dates with '5YS' frequency
    #date_ticks = pd.date_range(start=f'{start_year}-01-01', end=f'{end_year}-12-31', freq='5YS')
    
    date_ticks = pd.date_range(start=min_year, periods=((end_year-start_year)//5)+1, freq='5Y')

    print (date_ticks)
    
    # Format the x-axis to display dates.
    ax_precip.set_xticks(date_ticks)
    ax_precip.tick_params(axis='x', which='major', labelrotation=0)
    ax_precip.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))  # Format ticks as years.
    ax_precip.tick_params(axis='both', labelsize=11)  # Adjust the fontsize as needed


    # Grid
    ax_water.yaxis.grid(False)
    # Enable grid for x-axis with the specified locator as reference for gridlines
    ax_precip.grid(True, which='major', axis='x', linestyle='--', color='lightgrey', alpha=0.7)    
    
    
    # Include a legend.
    ax_water.legend(loc='upper right')
    ax_precip.legend(loc='upper left')
    
    # Adjust the plot to make room for the x-axis labels.
    fig.autofmt_xdate()    
    
    # Save the figure
    plt.savefig('bravura_waterlevel_precip.png', format='png')
    
    plt.show()
    



    
def main(target_lat, target_lon, data_directory):
    # Get the absolute path to the data directory
    directory = os.path.join(os.path.dirname(__file__), data_directory)

    sorted_data, all_time_data, all_precip_data = read_inputs(directory,target_lat,target_lon)


    #plot_monthly_precip_histogram(all_time_data, all_precip_data,target_lat,target_lon)
    #plot_monthly_precip(sorted_data, all_time_data, target_lat,target_lon)
    plot_yearly_precip(sorted_data, target_lat, target_lon)
    plot_waterlevel_yearly(all_time_data, all_precip_data, target_lat,target_lon)
    plot_combined_waterlevel_and_precip(sorted_data, target_lat, target_lon)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process precipitation data.")
    parser.add_argument("--lat", type=float, required=True, help="Latitude")
    parser.add_argument("--lon", type=float, required=True, help="Longitude")
    parser.add_argument("--data-directory", type=str, required=True, help="Relative path to data directory")
    args = parser.parse_args()

    main(args.lat, args.lon, args.data_directory)
    
    
    
    

