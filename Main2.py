import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from kalman_filter import kalman_filter

# ============================
# 1. Reading of the flight path
# ============================
file_path = r'C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\CODE TFG\all_lat_lon_2024_10_01_buf.csv'
df = pd.read_csv(file_path, delimiter=';')

callsign = df['callsign'].unique()[3]
df_flight = df[df['callsign'] == callsign].copy()

df_flight['latitude'] = df_flight['latitude'].str.replace(',', '.').astype(float)
df_flight['longitude'] = df_flight['longitude'].str.replace(',', '.').astype(float)

df_flight['groundspeed'] = df_flight['groundspeed'].astype(float)
df_flight['track'] = np.radians(df_flight['track'].str.replace(',', '.').astype(float))

df_flight['vx'] = df_flight['groundspeed'] * np.sin(df_flight['track'])
df_flight['vy'] = df_flight['groundspeed'] * np.cos(df_flight['track'])

original_lat = df_flight['latitude'].values
original_lon = df_flight['longitude'].values
vx = df_flight['vx'].values
vy = df_flight['vy'].values

ref_lat = original_lat[0]
ref_lon = original_lon[0]

corrected_latitudes, corrected_longitudes = kalman_filter(original_lat, original_lon, vx, vy, ref_lat, ref_lon)

# ============================
# 2. Plot the flight path and taxiway
# ============================
nodes_file = r'C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\CODE TFG\arlanda_airport_nodes.csv'
df_nodes = pd.read_csv(nodes_file, delimiter=';')

# Convertir latitudes y longitudes de los nodos (reemplazando coma por punto)
df_nodes['latitude'] = df_nodes['latitude'].str.replace(',', '.').astype(float)
df_nodes['longitude'] = df_nodes['longitude'].str.replace(',', '.').astype(float)

# Filtrar solo los nodos de taxiway
df_taxiways = df_nodes[df_nodes['type'] == 'taxiway'].copy()

# ============================
#  3. Select (slice) the points to be plotted
# (for example, from index 200 to 400)"
# ============================
# start_index = 0
# end_index = 50

# subset_original_lon = original_lon[start_index:end_index]
# subset_original_lat = original_lat[start_index:end_index]
# subset_corrected_lon = corrected_longitudes[start_index:end_index]
# subset_corrected_lat = corrected_latitudes[start_index:end_index]


plt.figure(figsize=(10, 6))

# Measured path
plt.plot(original_lat, original_lon, 'bo-', label='Measured')

# Corrected path
plt.plot(corrected_latitudes, corrected_longitudes, 'orange', marker='^', linestyle='-', label='Corrected')

# Taxiways
# plt.plot(df_taxiways['longitude'], df_taxiways['latitude'],
#          'o-', color='gray', markersize=3, linewidth=2, label='Taxiways')

plt.xlabel('Longitud')
plt.ylabel('Latitud')
plt.title('Ground Path for XFlight')
plt.legend()
plt.grid(False)
plt.show()