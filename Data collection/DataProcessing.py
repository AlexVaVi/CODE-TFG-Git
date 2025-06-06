import pandas as pd
import os
from traffic.data import airports
from traffic.core import Flight
from trim_parking import trim_parking
from shapely.geometry import LineString
from geopy.distance import geodesic
import matplotlib.pyplot as plt

# === FILE AND DATA LOADING ===

file_name = "Oct24_27_00am_24pm_All_ProcessedData.csv"
DATA_DIR = "C:\\Users\\alexv\\OneDrive\\Escritorio\\UPC\\TFG\\DATA\\October"

# Load airport geometry and filter to runway segments
df_airport = pd.read_csv(r'C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\arlanda_airport_nodes.csv')
df_airport = df_airport[df_airport['type'] == 'runway']

# Load raw OpenSky data
df = pd.read_csv(os.path.join(DATA_DIR, "Oct24_27_00pm_24pm_All.csv"))
df_new = df[['timestamp', 'callsign', 'latitude', 'longitude', 'groundspeed', 'track', 'onground', 'altitude', 'alert']]

# === DATA CLEANING ===

# Format timestamp
df_new['timestamp'] = pd.to_datetime(df_new['timestamp'])

# Remove empty callsigns
df_new = df_new[df_new['callsign'].notna()]
df_new = df_new[['timestamp', 'callsign', 'latitude', 'longitude', 'groundspeed', 'track', 'onground', 'altitude']]

# Filter out airborne points with altitude > 300 ft
df_new = df_new.query('onground | (altitude < 300)')

# Remove extreme groundspeed values (likely errors)
df_new = df_new[(df_new['groundspeed'].isna()) | (df_new['groundspeed'] < 200)]

# Remove callsigns with fewer than 180 points (minimum ~3 minutes of data)
df_new = df_new.groupby('callsign').filter(lambda group: len(group) >= 180)

# === FLIGHT SPLITTING ===

# Compute time difference between consecutive points per callsign
df_new['time_diff'] = df_new.groupby('callsign')['timestamp'].diff()

# Identify new flights if time gap > 3 minutes
df_new['new_flight_flag'] = (df_new['time_diff'] > pd.Timedelta(minutes=3)).astype(int)

# Number each individual flight attempt
df_new['flight_number'] = df_new.groupby('callsign')['new_flight_flag'].cumsum()

# Create a unique flight identifier
df_new['callsign_temp'] = df_new['callsign'] + '_' + df_new['flight_number'].astype(str)
df_new['callsign_group'] = pd.factorize(df_new['callsign_temp'])[0] + 1

# Remove flights longer than 1 hour (3600 points)
df_new = df_new.groupby('callsign_group').filter(lambda group: len(group) <= 3600)

# === RUNWAY CROSSING DETECTION ===

arlanda = airports['ESSA']
distance_tolerance_m = 5  # fallback tolerance

crossing_ids = []
runway_lines = []

# Build LineStrings from OSM runway segments
for rwy_id in df_airport['way_id'].unique():
    rwy_points = df_airport[df_airport['way_id'] == rwy_id].sort_values(by='node_id')
    coords = list(zip(rwy_points['longitude'], rwy_points['latitude']))
    if len(coords) >= 2:
        line = LineString(coords)
        runway_lines.append(line)

# Check each trajectory
for group_id in df_new['callsign_group'].unique():
    df_track = df_new[df_new['callsign_group'] == group_id].sort_values(by='timestamp')
    if df_track[['latitude', 'longitude']].dropna().shape[0] < 2:
        continue

    try:
        f = Flight(df_track)

        # Primary: intersect with official traffic library runways
        if f.intersects(arlanda.runways):
            crossing_ids.append(group_id)
            continue

        # Secondary: intersect with OSM LineStrings
        accepted = False
        for line in runway_lines:
            if f.intersects(line):
                crossing_ids.append(group_id)
                accepted = True
                break

        # Fallback: check distance to runway lines
        if not accepted:
            for line in runway_lines:
                flight_shape = f.shape
                distance_deg = flight_shape.distance(line)
                distance_m = distance_deg * 111000  # degrees to meters
                if distance_m <= distance_tolerance_m:
                    crossing_ids.append(group_id)
                    break

    except Exception as e:
        print(f"⚠️ Error in callsign_group {group_id}: {e}")

# Keep only the valid flights
df_new = df_new[df_new['callsign_group'].isin(crossing_ids)]

# === OPTIONAL: TRIM PARKING PHASE ===
# df_new = df_new.groupby('callsign_group').apply(trim_parking).reset_index(drop=True)

# Reassign callsign_group IDs to be sequential
df_new['callsign_group'] = pd.factorize(df_new['callsign_group'])[0] + 1

# Sort again by group and timestamp
df_new = df_new.sort_values(by=['callsign_group', 'timestamp'])

# Format timestamp to string for saving
df_new['timestamp'] = df_new['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

# Save cleaned and processed dataset
newdata = os.path.join(DATA_DIR, file_name)
df_new.to_csv(newdata, index=False, sep=',')

print(f"Data saved in '{newdata}'")


