import os

# Set environment variables for timezone data (required by pyarrow/parquet)
os.environ["PYARROW_TZDATA"] = r"C:\Users\alexv\anaconda3\envs\traffic\Lib\site-packages\tzdata"
os.environ["TZDATA"] = r"C:\Users\alexv\anaconda3\envs\traffic\Lib\site-packages\tzdata"

import pandas as pd
from traffic.data import airports, opensky

# --- Download flight data for ESSA airport (October 27, 2024) ---

flights = opensky.history(
    start="2024-10-27 00:00:00", 
    stop="2024-10-27 23:59:59",  
    bounds=airports["ESSA"],
)

# --- Save raw flight data ---

file_name = "Oct24_27_00pm_24pm_All.csv"
DATA_DIR = "C:\\Users\\alexv\\OneDrive\\Escritorio\\UPC\\TFG\\DATA\\October"

df_all = flights.data

# Select relevant columns
df = df_all[['callsign', 'latitude', 'longitude', 'groundspeed', 'track',
             'onground', 'timestamp', 'altitude', 'alert']]

# Save to CSV
newdata = os.path.join(DATA_DIR, file_name)
df.to_csv(newdata, index=False, sep=',')

# Confirmation messages
print(f"Data saved as '{newdata}'")
print(df_all.head())

# --- OPTIONAL FILTERING LOGIC (commented out) ---

# # Filter flights that intersect runways
# filtering_data = flights.intersects(airports["ESSA"].runways)

# # Keep only flights longer than 1 minute
# filtering_data = flights.longer_than("1 minute")

# # Keep only the longest segment of go-around attempts (below 400 ft)
# filtering_data = flights.query("altitude < 400").max_split()

# # Save filtered data
# filtered_df = filtering_data.data
# filtered_df = filtered_df[['callsign', 'latitude', 'longitude', 'groundspeed', 'track',
#                             'onground', 'timestamp', 'altitude', 'alert']]
# filtered_df.to_csv(os.path.join(DATA_DIR, "Oct24_20_00am_24pm_filtered.csv"), index=False, sep=',')
# print(f"Filtered data saved")
