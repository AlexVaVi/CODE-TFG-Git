import os
os.environ["PYARROW_TZDATA"] = r"C:\Users\alexv\anaconda3\envs\traffic\Lib\site-packages\tzdata"
os.environ["TZDATA"] = r"C:\Users\alexv\anaconda3\envs\traffic\Lib\site-packages\tzdata"

from traffic.data import opensky 
import pandas as pd
import pickle


# #Download data
# flights = opensky.history(
#     start="2024-01-03 10:00:00", 
#     stop="2024-01-03 21:59:59", 
#     departure_airport="ESSA", 
#     arrival_airport=None
# )

# #Save data
# with open("flights_data.pkl", "wb") as f:
#     pickle.dump(flights, f)

#Load data
with open("flights_data.pkl", "rb") as f:
    flights = pickle.load(f)

file_name = "Jan24_01_03_10am_22pm_Dep.csv"
DATA_DIR = "C:\\Users\\alexv\\OneDrive\\Escritorio\\UPC\\TFG\\DATA"

filtered_flights = flights.query('(altitude < 100)')

df_all = filtered_flights.data

df = df_all[['callsign', 'latitude', 'longitude', 'groundspeed', 'track','onground', 'timestamp', 'altitude', 'alert']]

#Verify data
print(df.head())

#Clean timestamp
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

#Clean callsign
df = df[df['callsign'].notna()]

df = df[['timestamp','callsign', 'latitude', 'longitude', 'groundspeed', 'track','onground','altitude']]

#Asign a group to each callsign
df['callsign_group'] = pd.factorize(df['callsign'])[0] + 1

df_sorted = df.sort_values(by=['callsign_group', 'timestamp'])

newdata = os.path.join(DATA_DIR, file_name)

df_sorted.to_csv(newdata, index=False, sep=',')

# Confirm data saved
print(f"Datos guardados en '{newdata}'")