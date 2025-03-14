import os
os.environ["PYARROW_TZDATA"] = r"C:\Users\alexv\anaconda3\envs\traffic\Lib\site-packages\tzdata"
os.environ["TZDATA"] = r"C:\Users\alexv\anaconda3\envs\traffic\Lib\site-packages\tzdata"

import pandas as pd
from traffic.data import airports, opensky

#Download data
flights = opensky.history(
    start="2024-10-20 00:00:00", 
    stop="2024-10-20 23:59:59",  
    bounds=airports["ESSA"],
)

file_name = "Oct24_20_00am_24pm_All.csv"
DATA_DIR = "C:\\Users\\alexv\\OneDrive\\Escritorio\\UPC\\TFG\\DATA\\October"

df_all = flights.data

df = df_all[['callsign', 'latitude', 'longitude', 'groundspeed', 'track','onground', 'timestamp', 'altitude', 'alert']]

#Verify data
print(df.head())

newdata = os.path.join(DATA_DIR, file_name)

df.to_csv(newdata, index=False, sep=',')

# Confirm data saved
print(f"Data saved as '{newdata}'")

# #Filtering data

# # each trajectory must cross the runways
# filtering_data = flights.intersects(airports["ESSA"].runways)
# # only keep trajectories with more than one minute of data
# filtering_data = flights.longer_than("1 minute")
# # only keep the successful attempt when go around
# # i.e., the longest interval of consecutive data below 400ft
# filtering_data = flights.query("altitude < 400").max_split()

# filtered_df = filtering_data.data
# filtered_df = filtered_df[['callsign', 'latitude', 'longitude', 'groundspeed', 'track','onground', 'timestamp', 'altitude', 'alert']]
# filtered_df.to_csv(os.path.join(DATA_DIR, "Oct24_20_00am_24pm_filtered.csv"), index=False, sep=',')

# print(f"Data filtered saved")