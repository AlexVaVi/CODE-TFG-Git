import folium
import pandas as pd
import numpy as np
import webbrowser
import flight_path as fp
import classify_flight as cf
import flights_path_type as fpt
from shapely.geometry import LineString, Point
from HotspotsMethod1 import hotspots1, visualize_hotspots1
from HotspotsMethod2 import hotspots2, visualize_hotspots2
from datetime import datetime
from ParkingDetection import find_parking
from ground_time import ground_time
from kalman_filter import kalman_filter
from flightpath_smoother import flight_path_smoother
import folium 
from ApronAnalysis import find_apron
import matplotlib.pyplot as plt

#Data
file_path = r'C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\October\Oct24_25_00am_24pm_All_ProcessedData.csv'
df_flight = pd.read_csv(file_path, delimiter=',')
df_airport = pd.read_csv(r'C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\arlanda_airport_nodes.csv', delimiter=',')
df_airport = df_airport[df_airport['type'] == 'runway']
df_parkings = pd.read_csv(r'C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\arlanda_parking_nodes.csv', delimiter=',')
df_apron = pd.read_csv(r'C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\arlanda_airport_nodes.csv', delimiter=',')
df_apron = df_apron[df_apron['type'] == 'apron']



#AIRPORT RUNWAYS#
##################

runway_lines = []

for rwy_id in df_airport['way_id'].unique():
    rwy_points = df_airport[df_airport['way_id'] == rwy_id].sort_values(by='node_id')  # ajusta si tienes otro orden

    coords = list(zip(rwy_points['longitude'], rwy_points['latitude']))
    if len(coords) >= 2:
        line = LineString(coords)
        runway_lines.append(line)
        
##################

#AIRPORT PARKING#
##################

parking_lines = []

for parking_id in df_parkings['Way ID'].unique():
    parking_points = df_parkings[df_parkings['Way ID'] == parking_id].sort_values(by='Node ID')  # ajusta si necesitas otro criterio

    coords = list(zip(parking_points['Longitude'], parking_points['Latitude']))
    line = LineString(coords)
    parking_lines.append(line)
        
##################



#PARKING
# flight_type, closest_parking, distance = find_parking(df_flight, callsign_nr, parking_lines, df_apron)
# print(f"Flight type: {flight_type}, Closest parking: {closest_parking}")

#HOTSPOTS

start = datetime(2024, 10, 20, 15, 0, 0)  
end   = datetime(2024, 10, 20, 16, 0, 0)  

# df_flight['timestamp'] = pd.to_datetime(df_flight['timestamp'])
# df = df_flight.sort_values(by='timestamp')
# if start is not None and end is not None:
#         df = df[(df['timestamp'] >= start) & (df['timestamp'] <= end)]
# print(len(df))

#Method 1
# hotspots_df = hotspots1(df_flight, runway_lines, start_time=start, end_time=end)
# print(len(hotspots_df))
# visualize_hotspots1(hotspots_df, map_filename='hotspots1.html')
# webbrowser.open('hotspots1.html')

#Method 2
# hotspots_df = hotspots2(df_flight, start_time=start, end_time=end)
# hotspots_level0 = hotspots_df[hotspots_df['level'] == 0]
# hotspots_level1 = hotspots_df[hotspots_df['level'] == 1]
# hotspots_level2 = hotspots_df[hotspots_df['level'] == 2]
# hotspots_level3 = hotspots_df[hotspots_df['level'] == 3]
# hotspots_level4 = hotspots_df[hotspots_df['level'] == 4]
# hotspots_level5 = hotspots_df[hotspots_df['level'] == 5]
# tot0 = len(hotspots_level0)
# tot1 = len(hotspots_level1)
# tot2 = len(hotspots_level2)
# tot3 = len(hotspots_level3)
# tot4 = len(hotspots_level4)
# tot5 = len(hotspots_level5)
# print(tot0, tot1, tot2, tot3, tot4, tot5)
# visualize_hotspots2(hotspots_df, map_filename='hotspots2.html')
# webbrowser.open('hotspots2.html')

# callsign_nr = 2
# df_flightKalman = df_flight[df_flight['callsign_group'] == callsign_nr].copy()
# callsign = df_flightKalman['callsign'].unique()[0]


#GROUND TIME
# contador1Dep = 0
# contador2Dep = 0
# contador3Dep = 0

# contador1Arr = 0
# contador2Arr = 0
# contador3Arr = 0

# runwaytime, taxitime, used_runway = ground_time(df_flight, df_apron, runway_lines, callsign_nr)
# type = cf.classify_flight(df_flight, callsign_nr, df_apron)
# __path__ = fp.flight_path(df_flight, callsign_nr, df_apron)
# print(f" Runway used: {used_runway}")
# print(f"Type: {type}")

# for callsign_nr in range(1, df_flight['callsign_group'].max() + 1):
#     runwaytime, taxitime, used_runway = ground_time(df_flight, df_apron, runway_lines, callsign_nr)
#     type = cf.classify_flight(df_flight, callsign_nr, df_apron)
#     # parking = find_parking(df_flight, callsign_nr, parking_lines, df_apron)
#     # print(f"Taxi time: {taxitime}, Runway time: {runwaytime}, Used runway: {used_runway}, Parking: {parking}")
#     # path = fp.flight_path(df_flight, callsign_nr, df_apron)

#     # __path__ = fp.flight_path(df_flight, callsign_nr, df_apron)
    
#     if used_runway == 1:
#         if type == "Arrival":
#             contador1Arr += 1
#         elif type == "Departure":
#             contador1Dep += 1
#     elif used_runway == 2:
#         if type == "Arrival":
#             contador2Arr += 1
#         elif type == "Departure":
#             contador2Dep += 1
#     elif used_runway == 3:
#         if type == "Arrival":
#             contador3Arr += 1
#         elif type == "Departure":
#             contador3Dep += 1
            
# Total = contador1Arr + contador2Arr + contador3Arr + contador1Dep + contador2Dep + contador3Dep
# print("Contador 1 Arrival:", contador1Arr)
# print("Contador 1 Departure:", contador1Dep)
# print("Contador 2 Arrival:", contador2Arr)
# print("Contador 2 Departure:", contador2Dep)
# print("Contador 3 Arrival:", contador3Arr)
# print("Contador 3 Departure:", contador3Dep)
# print("Total:", Total)

#CORRECTED PATH

# ref_lat = df_flight['latitude'].values[0]
# ref_lon = df_flight['longitude'].values[0]

# path = fp.flight_path(df_flight, callsign_nr, df_apron)

# corrected_latitudes, corrected_longitudes, closest_segments = kalman_filter(df_flightKalman, ref_lat, ref_lon)
# df_corrected = pd.DataFrame({
#     'timestamp': df_flightKalman['timestamp'],
#     'callsign': df_flightKalman['callsign'],
#     'latitude': corrected_latitudes,
#     'longitude': corrected_longitudes,
#     'callsign_group': df_flightKalman['callsign_group']
# })

# smooth_path = flight_path_smoother(corrected_latitudes, corrected_longitudes, closest_segments, ref_lat, ref_lon)

# legend_html = f"""
# <div style="position: fixed; 
#             top: 20px; right: 20px; width: 190px; height: 110px; 
#             background-color: white; z-index:9999; font-size:14px; 
#             padding: 10px; border-radius:5px; box-shadow:2px 2px 6px rgba(0,0,0,0.5);">
#     <b> {flight_type}</b>: {callsign}<br><br>
#     🅿️ <b>Parking: {closest_parking}<br>
#     🛬 <b>Taxi time:</b> {taxitime:.1f} s<br>
#     🛫 <b>Runway time:</b> {runwaytime:.1f} s
# </div>
# """

# # Ruta del HTML que ya tienes
# html_path = "flight_path_smoother.html"

# # Leer el contenido
# with open(html_path, "r", encoding="utf-8") as f:
#     html = f.read()

# # Insertar la leyenda justo antes del </body>
# html = html.replace("</body>", legend_html + "\n</body>")

# # Guardar el HTML modificado
# with open(html_path, "w", encoding="utf-8") as f:
#     f.write(html)

# print("✅ Leyenda añadida con éxito al HTML.")




#RUNWAY OCCUPANCY TIME

results = []

for callsign_nr in df_flight['callsign_group'].unique():
    try:
        runway_time, taxi_time, used_runway, t_start, t_end = ground_time(df_flight, df_apron, runway_lines, callsign_nr)

        if used_runway is None or t_start is None or t_end is None:
            continue  

        results.append({
            "callsign": callsign_nr,
            "used_runway": used_runway,
            "runway_time": runway_time,
            "t_start": t_start,
            "t_end": t_end
        })

    except Exception as e:
        print(f"Error with callsign {callsign_nr}: {e}")
        continue
    
df_usage = pd.DataFrame(results)

active_ops = []

for i, row in df_usage.iterrows():
    t_start_i = row['t_start']
    t_end_i = row['t_end']

    # Comptem quants altres vols se solapen amb aquest interval
    count = df_usage[
        (df_usage['t_end'] >= t_start_i) & (df_usage['t_start'] <= t_end_i)
    ].shape[0]  # Número de files que se solapen

    active_ops.append(count)

df_usage['active_operations'] = active_ops

df_usage.to_csv("runway_usage_stats.csv", index=False)
print("✅ Dades guardades a 'runway_usage_stats.csv'")
  
  



