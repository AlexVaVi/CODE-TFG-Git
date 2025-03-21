import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from kalman_filter import kalman_filter
import flight_path as fp
from scipy.interpolate import splrep, splev
import flightpath_smoother as fs
import segments as sg


# ============================
# 1. Reading of the flight path
# ============================
file_path = r'C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\October\NSZ4363_KalmanTest.csv'
df_flight = pd.read_csv(file_path, delimiter=',')
df_airport = pd.read_csv(r'C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\arlanda_airport_nodes.csv', delimiter=',')
df_airport = df_airport[df_airport['type'] == 'runway']
df_flight = df_flight[df_flight['onground']]

original_lat = df_flight['latitude'].values
original_lon = df_flight['longitude'].values

ref_lat = original_lat[0]
ref_lon = original_lon[0]

corrected_latitudes, corrected_longitudes, closest_segments = kalman_filter(df_flight, ref_lat, ref_lon)
df_corrected = pd.DataFrame({
    'timestamp': df_flight['timestamp'],
    'callsign': df_flight['callsign'],
    'latitude': corrected_latitudes,
    'longitude': corrected_longitudes,
    'callsign_group': df_flight['callsign_group']
})

# ============================
# 2. Plotting measured and corrected path
# ============================

callsign_nr = 1

path = fp.flight_path(df_flight, callsign_nr, df_airport)
# print(df_corrected)
# path_corrected = fp.flight_path(df_corrected, callsign_nr, df_airport)

smoothpath = fs.flight_path_smoother(corrected_latitudes, corrected_longitudes, closest_segments, ref_lat, ref_lon)
# segmentpath = sg.plot_segments(closest_segments, ref_lat, ref_lon)