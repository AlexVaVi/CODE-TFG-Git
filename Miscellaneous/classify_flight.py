import math
import pandas as pd
from Haversine import haversine
from ApronAnalysis import find_apron

def classify_flight(trajectory_df, callsign_nr, df_apron_nodes):

    trajectory_df = trajectory_df[(trajectory_df['callsign_group'] == callsign_nr)]
        
    if trajectory_df.empty:
        return "Unknown"

    # Get first and last points
    first_point = trajectory_df.iloc[0]
    last_point = trajectory_df.iloc[-1]

    # Check if either point is inside any apron polygon
    first_in_apron = find_apron(first_point['latitude'], first_point['longitude'], df_apron_nodes)
    last_in_apron = find_apron(last_point['latitude'], last_point['longitude'], df_apron_nodes)

    # Apply logic based on apron presence
    if first_in_apron is not None and last_in_apron is None:
        return "Departure"
    elif last_in_apron is not None and first_in_apron is None:
        return "Arrival"
    else:
        return "Unknown"
