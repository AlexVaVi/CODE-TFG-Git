import pandas as pd
import os
from traffic.data import airports
from traffic.core import Flight
from trim_parking import trim_parking
from shapely.geometry import LineString, Point
from geopy.distance import geodesic
import matplotlib.pyplot as plt


file_name = "Oct24_27_00am_24pm_All_ProcessedData.csv"
DATA_DIR = "C:\\Users\\alexv\\OneDrive\\Escritorio\\UPC\\TFG\\DATA\\October"
df_airport = pd.read_csv(r'C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\arlanda_airport_nodes.csv', delimiter=',')
df_airport = df_airport[df_airport['type'] == 'runway']

df = pd.read_csv(os.path.join(DATA_DIR, "Oct24_27_00pm_24pm_All.csv"), delimiter=',')

df_new = df[['timestamp','callsign', 'latitude', 'longitude', 'groundspeed', 'track', 'onground', 'altitude', 'alert']]

#clean timestamp
df_new['timestamp'] = pd.to_datetime(df_new['timestamp'])   

#Clean callsign
df_new = df_new[df_new['callsign'].notna()]
df_new = df_new[['timestamp','callsign', 'latitude', 'longitude', 'groundspeed', 'track', 'onground', 'altitude']]

#Clean groundspeed
# df_new = df_new[df_new['groundspeed'].notna()]

#Clean altitude
df_new = df_new.query('onground | (altitude < 300)')

#Clean groundspeed
df_new = df_new[(df_new['groundspeed'].isna()) | (df_new['groundspeed'] < 200)]

#Clean track
# df_new = df_new[df_new['track'].notna()]

#At least 3 minutes of data    
df_new = df_new.groupby('callsign').filter(lambda group: len(group) >= 180)

# Calculate time difference between consecutive points per callsign
df_new['time_diff'] = df_new.groupby('callsign')['timestamp'].diff()

# Flag new flights when time gap exceeds 3 minutes
df_new['new_flight_flag'] = (df_new['time_diff'] > pd.Timedelta(minutes=3)).astype(int)

# Create flight number counter within each callsign group
df_new['flight_number'] = df_new.groupby('callsign')['new_flight_flag'].cumsum()

# Combine callsign and flight number to uniquely identify each flight
df_new['callsign_temp'] = df_new['callsign'] + '_' + df_new['flight_number'].astype(str)

# Assign numeric callsign_group
df_new['callsign_group'] = pd.factorize(df_new['callsign_temp'])[0] + 1

# #Maximum 1h of data
df_new = df_new.groupby('callsign_group').filter(lambda group: len(group) <= 3600)



arlanda = airports['ESSA']

distance_tolerance_m = 5  # meters

# Check which trajectories intersect runways
crossing_ids = []

# Get only the shapely geometries of runway objects
runway_lines = []

for rwy_id in df_airport['way_id'].unique():
    rwy_points = df_airport[df_airport['way_id'] == rwy_id].sort_values(by='node_id')  # ajusta si tienes otro orden

    coords = list(zip(rwy_points['longitude'], rwy_points['latitude']))
    if len(coords) >= 2:
        line = LineString(coords)
        runway_lines.append(line)

for group_id in df_new['callsign_group'].unique():
    df_track = df_new[df_new['callsign_group'] == group_id].sort_values(by='timestamp')

    if df_track[['latitude', 'longitude']].dropna().shape[0] < 2:
        continue

    try:
        f = Flight(df_track)

        # Primary filter: official airport runways from traffic
        if f.intersects(arlanda.runways):
            crossing_ids.append(group_id)
            continue

        # Secondary filter: intersection with LineString runways from OpenstreetMap data
        accepted = False
        for line in runway_lines:
            if f.intersects(line):
                crossing_ids.append(group_id)
                accepted = True
                break
        
        # Fallback: check distance to runway lines
        if not accepted:
            for line in runway_lines:
                flight_shape = f.shape  # shapely LineString of flight path
                distance_deg = flight_shape.distance(line)
                distance_m = distance_deg * 111000  # convert to meters

                if distance_m <= distance_tolerance_m:
                    crossing_ids.append(group_id)
                    accepted = True
                    break

    except Exception as e:
        print(f"⚠️ Error in callsign_group {group_id}: {e}")
        
# Identify removed callsign_groups and callsigns
# removed_ids = df_new.loc[~df_new['callsign_group'].isin(crossing_ids), 'callsign_group'].unique()
# removed_callsigns = df_new.loc[~df_new['callsign_group'].isin(crossing_ids), 'callsign'].unique()

# print("\n⛔ Callsign_groups removed (did not cross any runway):", removed_ids.tolist())
# print("⛔ Corresponding callsigns:", removed_callsigns.tolist())
# print(len(removed_ids))
# print(len(removed_callsigns))

# Keep only flights that cross a runway
df_new = df_new[df_new['callsign_group'].isin(crossing_ids)]


#Trim parking
# df_new = df_new.groupby('callsign_group').apply(trim_parking).reset_index(drop=True)

#Recalculate callsign group to make it consecutive
df_new['callsign_group'] = pd.factorize(df_new['callsign_group'])[0] + 1

# Sort again by callsign_group and timestamp
df_new = df_new.sort_values(by=['callsign_group', 'timestamp'])

#Convert to string
df_new['timestamp'] = df_new['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

newdata = os.path.join(DATA_DIR, file_name)

df_new.to_csv(newdata, index=False, sep=',')

# Confirm data saved
print(f"Data saved in '{newdata}'")

