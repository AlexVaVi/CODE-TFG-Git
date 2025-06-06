import folium
import pandas as pd
import numpy as np
import webbrowser
from datetime import time
import flight_path as fp
import classify_flight as cf
import flights_path_type as fpt
from shapely.geometry import LineString, Point
from HotspotsMethod1 import hotspots1, visualize_hotspots1
from HotspotsMethod2 import hotspots2, visualize_hotspots2
from datetime import datetime
from ParkingDetection import find_parking
from ground_time import ground_time
from smoother_filter import smoother_filter
from shapely.geometry import MultiPoint
from flightpath_smoother import flight_path_smoother
import folium 
from collections import Counter
from ApronAnalysis import find_apron
import matplotlib.pyplot as plt
from GateOccupancy import compute_gate_blocked_intervals, plot_gate_occupancy_chart, plot_gate_occupancy_by_operations, remove_overlaps_by_gate, compute_hourly_gate_occupancy_avg_from_folder, plot_avg_gate_occupancy, get_unique_gates_from_folder, plot_gate_occupancy_comparison
from RunwayGate import add_runways_to_occupancy
import glob
import os
from Figures.SeparationOperations import calculate_separation_times, plot_separation_times
from MeanSeparation import separation_data, plot_separation_summary

# === Load Data ===

# Define base path to your local dataset directory
# BASE_DATA_PATH = r'path_to_your_data_directory'  # <-- Replace with your actual base path

# # Load processed flight data
# flight_data_file = os.path.join(BASE_DATA_PATH, 'October', 'Oct24_20_00am_24pm_All_ProcessedData.csv')
# df_flight = pd.read_csv(flight_data_file)

# # Load full airport node data
# airport_nodes_file = os.path.join(BASE_DATA_PATH, 'arlanda_airport_nodes.csv')
# df_airport_nodes = pd.read_csv(airport_nodes_file)

# # Extract runway node data
# df_runways = df_airport_nodes[df_airport_nodes['type'] == 'runway']

# # Extract apron node data
# df_aprons = df_airport_nodes[df_airport_nodes['type'] == 'apron']

# # Load parking node data
# parking_nodes_file = os.path.join(BASE_DATA_PATH, 'arlanda_parking_nodes.csv')
# df_parkings = pd.read_csv(parking_nodes_file)




#AIRPORT RUNWAYS#
##################

# runway_lines = []

# for rwy_id in df_airport['way_id'].unique():
#     rwy_points = df_airport[df_airport['way_id'] == rwy_id].sort_values(by='node_id')  # ajusta si tienes otro orden

#     coords = list(zip(rwy_points['longitude'], rwy_points['latitude']))
#     if len(coords) >= 2:
#         line = LineString(coords)
#         runway_lines.append(line)
        
##################

#AIRPORT PARKING#
##################

# parking_lines = []

# for parking_id in df_parkings['Way ID'].unique():
#     parking_points = df_parkings[df_parkings['Way ID'] == parking_id].sort_values(by='Node ID')  # ajusta si necesitas otro criterio

#     coords = list(zip(parking_points['Longitude'], parking_points['Latitude']))
#     line = LineString(coords)
#     parking_lines.append(line)

##################


##################
# BOTTLENECKS #
##################

# days = range(20, 28)  # del 20 al 27
# mode ="Departure"      # "arrival", "departure", "all"
# target_runway = 1
# target_gates = {84}

# path_groundtime = r"C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\October\GroundTime"
# path_flightdata = r"C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\October"

# total_count = 0
# sas_count = 0
# nsz_count = 0
# ryr_count = 0
# dlh_count = 0
# fin_count = 0

# for day in days:
#     try:
#         # === Archivos por día ===
#         gt_path = os.path.join(path_groundtime, f"groundtime_stats{day}.csv")
#         fl_path = os.path.join(path_flightdata, f"Oct24_{day}_00am_24pm_All_ProcessedData.csv")

#         print(f"📁 Processing {day}...")

#         df_stats = pd.read_csv(gt_path)
#         df_flight = pd.read_csv(fl_path)

#         df_stats = df_stats[df_stats['used_runway'] == target_runway]
#         callsigns = df_stats['callsign'].unique()

#         count_day = 0
#         for callsign_nr in callsigns:
#             try:
#                 flight_type, closest_parking, distance = find_parking(df_flight, callsign_nr, parking_lines, df_apron)
                
#                 match = df_flight[df_flight['callsign_group'] == callsign_nr]
#                 if match.empty or closest_parking is None or flight_type is None:
#                     continue

#                 if int(closest_parking) not in target_gates:
#                     continue

#                 if mode != "all" and flight_type.lower() != mode.lower():
#                     continue

#                 t_start = pd.to_datetime(match.iloc[0]['timestamp'])
#                 if not time(6, 0) <= t_start.time() <= time(19, 0):
#                     continue
                
#                 base_callsign = match.iloc[0]['callsign']
#                 if isinstance(base_callsign, str):
#                     if base_callsign.startswith('SAS'):
#                         sas_count += 1
#                         print(base_callsign)
#                     elif base_callsign.startswith('NSZ'):
#                         nsz_count += 1
#                     elif base_callsign.startswith('RYR'):
#                         ryr_count += 1
#                     elif base_callsign.startswith('DLH'):
#                         dlh_count += 1
#                     elif base_callsign.startswith('FIN'):
#                         fin_count += 1
                    
#                 count_day += 1

#             except Exception as e:
#                 print(f"⚠️ Error {callsign_nr}: {e}")

#         print(f"✅ Day {day}: {count_day} valid flights")
#         total_count += count_day

#     except Exception as e:
#         print(f"❌ Error {day}: {e}")

# print(f"\n🎯 Total valid flights: {total_count}")
# print(f"  ├ SAS: {sas_count}")
# print(f"  ├ NSZ: {nsz_count}")
# print(f"  ├ RYR: {ryr_count}")
# print(f"  ├ DLH: {dlh_count}")
# print(f"  └ FIN: {fin_count}")


#PARKING
# flight_type, closest_parking, distance = find_parking(df_flight, callsign_nr, parking_lines, df_apron)
# print(f"Flight type: {flight_type}, Closest parking: {closest_parking}")


#HOTSPOTS

# start = datetime(2024, 10, 20, 5, 0, 0)  
# end   = datetime(2024, 10, 20, 6, 0, 0)  

# df_flight['timestamp'] = pd.to_datetime(df_flight['timestamp'])
# df = df_flight.sort_values(by='timestamp')
# if start is not None and end is not None:
#         df = df[(df['timestamp'] >= start) & (df['timestamp'] <= end)]
# print(len(df))

# Method 1
# hotspots_df = hotspots1(df_flight, runway_lines, start_time=start, end_time=end)
# print(len(hotspots_df))
# visualize_hotspots1(hotspots_df, map_filename='hotspots1.html')
# webbrowser.open('hotspots1.html')

#Method 2
# hotspots_df = hotspots2(df_flight, runway_lines, start_time=start, end_time=end)
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

# callsign_nr = 48
# df_flightSmooth = df_flight[df_flight['callsign_group'] == callsign_nr].copy()
# callsign = df_flightSmooth['callsign'].unique()[0]

# ref_lat = df_flightSmooth['latitude'].values[0]
# ref_lon = df_flightSmooth['longitude'].values[0]

# corrected_latitudes, corrected_longitudes, closest_segments = smoother_filter(df_flightSmooth, ref_lat, ref_lon)
# df_corrected = pd.DataFrame({
#     'timestamp': df_flightSmooth['timestamp'],
#     'callsign': df_flightSmooth['callsign'],
#     'latitude': corrected_latitudes,
#     'longitude': corrected_longitudes,
#     'callsign_group': df_flightSmooth['callsign_group']
# })

# smooth_path = flight_path_smoother(corrected_latitudes, corrected_longitudes, closest_segments, ref_lat, ref_lon, df_flightSmooth)

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


# html_path = "flight_path_smoother.html"

# with open(html_path, "r", encoding="utf-8") as f:
#     html = f.read()

# html = html.replace("</body>", legend_html + "\n</body>")

# with open(html_path, "w", encoding="utf-8") as f:
#     f.write(html)

# print("✅")




# RUNWAY & TAXI TIME

# results = []

# for callsign_nr in df_flight['callsign_group'].unique():
#     try:
#         runway_time, taxi_time, used_runway, t_start, t_end = ground_time(df_flight, df_apron, runway_lines, callsign_nr)

#         if used_runway is None or t_start is None or t_end is None:
#             continue  

#         results.append({
#             "callsign": callsign_nr,
#             "used_runway": used_runway,
#             "runway_time": runway_time,
#             "taxi_time": taxi_time,
#             "t_start": t_start,
#             "t_end": t_end,
#         })

#     except Exception as e:
#         print(f"Error with callsign {callsign_nr}: {e}")
#         continue
    
# df_usage = pd.DataFrame(results)

# df_usage.to_csv("groundtime_stats27.csv", index=False)
# print("✅ Data saved 'groundtime_stats.csv'")
  
#(TAXIING)

# df_usage = pd.read_csv("groundtime_stats27.csv", parse_dates=["t_start", "t_end"])
# df_usage['t_start'] = pd.to_datetime(df_usage['t_start'])
# df_flight['timestamp'] = pd.to_datetime(df_flight['timestamp']) 

# df_flight['hour'] = df_flight['timestamp'].dt.floor('h')
# df_usage['hour'] = df_usage['t_start'].dt.floor('h')


# ops_per_hour = df_flight.groupby('hour').agg(
#     total_operations=('callsign_group', 'nunique') 
# ).reset_index()

# median_taxi_time = df_usage.groupby(['used_runway', 'hour']).agg(
#     median_taxi_time=('taxi_time', 'median')
# ).reset_index()

# result = pd.merge(median_taxi_time, ops_per_hour, on='hour', how='left')

# result.to_csv('taxiing_hourly_stats27.csv', index=False)
# print("✅")

#(RUNWAY)

# df_usage = pd.read_csv("groundtime_stats27.csv", parse_dates=["t_start", "t_end"])
# df_usage['t_start'] = pd.to_datetime(df_usage['t_start'])
# df_flight['timestamp'] = pd.to_datetime(df_flight['timestamp']) 

# df_flight['hour'] = df_flight['timestamp'].dt.floor('h')
# df_usage['hour'] = df_usage['t_start'].dt.floor('h')


# ops_per_hour = df_flight.groupby('hour').agg(
#     total_operations=('callsign_group', 'nunique')  # número de operaciones reales
# ).reset_index()

# median_runway_time = df_usage.groupby(['used_runway', 'hour']).agg(
#     median_runway_time=('runway_time', 'median')
# ).reset_index()

# result = pd.merge(median_runway_time, ops_per_hour, on='hour', how='left')

# result.to_csv('runway_hourly_stats27.csv', index=False)
# print("✅")


## GATE OCCUPANCY ##
####################

# df_occupancy = compute_gate_blocked_intervals(df_flight, parking_lines, df_apron)

# print("Total d'operacions analitzades:", len(df_occupancy))
# df_occupancy = df_occupancy[df_occupancy['duration_minutes'] >= 1]
# df_occupancy = remove_overlaps_by_gate(df_occupancy)

# folder_path = r"C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\October\GateOccupancy"

# avg_hourly = compute_hourly_gate_occupancy_avg_from_folder(folder_path)
# plot_avg_gate_occupancy(avg_hourly, max_capacity=28)

# plot_occupancy = plot_gate_occupancy_comparison(folder_path)


#USUAL CAPACITY

# gates, total = get_unique_gates_from_folder(folder_path)

# print(f"🔢 Gates identified in the week: {total}")
# print(f"Gates: {gates}")

#PLOT

# GatePlot = plot_gate_occupancy_chart(df_occupancy, top_n=10)
# OpGatePlot = plot_gate_occupancy_by_operations(df_occupancy, top_n=10)

#RUNWAY USED PER GATE

# folder = r"C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\October\GateOccupancy"
# df_occupancy = pd.read_csv(os.path.join(folder, "GateOccupancy27.csv"), delimiter=',')

# df_occupancy['start_time'] = pd.to_datetime(df_occupancy['start_time'])
# df_occupancy['end_time'] = pd.to_datetime(df_occupancy['end_time'])
# df_occupancy = df_occupancy[df_occupancy['duration_minutes'] >= 1]

# # df_occupancy = remove_overlaps_by_gate(df_occupancy)
# df_occupancy_week = add_runways_to_occupancy(df_occupancy, df_flight, runway_lines, df_apron)
# df_occupancy_week.to_csv(os.path.join(folder, "GateOccupancy27.csv"), index=False)

# df_occupancy_week.to_csv(folder, index=False)





## SEPARATION OPERATIONS ##
####################

# path = r"C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\October\RunwayUsage\Usage"

# separation = calculate_separation_times(path)

# for runway in separation.keys():
#     separation[runway] = separation[runway][separation[runway] <= 500]
    
# print(f"{'Runway':<10} {'Count':<6} {'Mean (s)':<10} {'Median (s)':<12} {'Std Dev (s)':<12} {'P25':<8} {'P75':<8}")

# for rwy, values in separation.items():
#     values = np.array(values)
#     print(f"{rwy:<10} {len(values):<6} {np.mean(values):<10.1f} {np.median(values):<12.1f} {np.std(values):<12.1f} "
#           f"{np.percentile(values, 25):<8.1f} {np.percentile(values, 75):<8.1f}")
    
# plot = plot_separation_times(separation, bin_width=10)


#####

# path = r"C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\CODE-TFG Git"

# mean_separation = separation_data(path, "separation_stats.csv", bin_size=5)

# plot_separation_summary(os.path.join(path, "separation_stats.csv"))
