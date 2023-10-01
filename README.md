# pt_precipitation_analysis
This repo contains the analysis of precipitation data for Portugal in the period of 1950-2003

The dataset is provided inside the ipma/ folder and the script in src/ipma_pt2_plot.py does a simple analysis of the monthly and yearly precipitation for the coordinates you provide.

To run the script you just need to have python 3.8 or higher installed in your environment. Simply find the coordinateds of your desired location and run the script in the following way

`cd pt_precipitation_analysis/src`

`./ipma_pt2_plot.py --lat 'targer lat' --lon 'target lon' --data-directory 'relative path to data'`

example:

`run ipma_pt2_plot.py --lat 37.24 --lon -8.70 --data-directory ../ipma/mensal/`
