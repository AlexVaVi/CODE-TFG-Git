import pandas as pd
import os

file_name = "Oct24_20_00am_24pm_All_onground_clean.csv"
DATA_DIR = "C:\\Users\\alexv\\OneDrive\\Escritorio\\UPC\\TFG\\DATA\\October"

df = pd.read_csv(os.path.join(DATA_DIR, "Oct24_20_00am_24pm_All.csv"), delimiter=',')

df_new = df[['timestamp','callsign', 'latitude', 'longitude', 'groundspeed', 'track', 'onground', 'altitude', 'alert']]

#clean timestamp
df_new['timestamp'] = pd.to_datetime(df_new['timestamp'])   

#Clean callsign
df_new = df_new[df_new['callsign'].notna()]
df_new = df_new[['timestamp','callsign', 'latitude', 'longitude', 'groundspeed', 'track', 'onground', 'altitude']]

#Clean groundspeed
df_new = df_new[df_new['groundspeed'].notna()]

#Clean altitude
df_new = df_new.query('onground | (altitude < 300)')

#Clean track
df_new = df_new[df_new['track'].notna()]

#At least 40 seconds of data    
df_new = df_new.groupby('callsign').filter(lambda group: len(group) >= 40)
#Maximum 1h of data
df_new = df_new.groupby('callsign').filter(
    lambda x: (x['timestamp'].iloc[-1] - x['timestamp'].iloc[0]).total_seconds() <= 3600
)

#Asign a group to each callsign
df_new['callsign_group'] = pd.factorize(df_new['callsign'])[0] + 1

df_new = df_new.sort_values(by=['callsign_group', 'timestamp'])

#Convert to string
df_new['timestamp'] = df_new['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

newdata = os.path.join(DATA_DIR, file_name)

df_new.to_csv(newdata, index=False, sep=',')

# Confirm data saved
print(f"Data saved in '{newdata}'")

