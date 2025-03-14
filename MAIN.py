import folium
import pandas as pd
import numpy as np
import webbrowser
import flight_path as fp
import classify_flight as cf
import flights_path_type as fpt

#Data
file_path = r'C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\October\Oct24_20_00am_24pm_All_onground_clean.csv'
df_flight = pd.read_csv(file_path, delimiter=',')
df_airport = pd.read_csv(r'C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\arlanda_airport_nodes.csv', delimiter=',')
df_airport = df_airport[['type', 'latitude', 'longitude']]
df_airport = df_airport[df_airport['type'] == 'runway']

#Callsign number
callsign_nr = 3

# print(df_flight['callsign_group'].iloc[-1])

#Flightpath
path = fp.flight_path(df_flight, callsign_nr, df_airport)

# #Type flight
# type = cf.classify_flight(df_flight, callsign_nr, df_airport)
# print(type)

# callsign_limit = 10

#Arrival flight paths
# arrival_paths = fpt.plot_flights_by_classification(df_flight, df_airport, callsign_limit, desired_classification="Arrival",  zoom_start=16, output_html="arrival_flights_map.html")

# #Departure flight paths
# departure_paths = fpt.plot_flights_by_classification(df_flight, df_airport, callsign_limit, desired_classification="Departure", zoom_start=16, output_html="departure_flights_map.html")