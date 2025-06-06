from shapely.geometry import Point
from classify_flight import classify_flight
from ApronAnalysis import find_apron
import pandas as pd

def runway_condition(lat, lon, runway_lines, threshold=4, mode="near"):
    """
    Checks whether a point is near or far from any runway line.
    
    Parameters:
        - mode = "near": returns True if point is ≤ threshold meters from any runway
        - mode = "far":  returns True if point is > threshold meters from all runways
    """
    point = Point(lon, lat)
    for line in runway_lines:
        distance = point.distance(line) * 111000  # convert degrees to meters
        if mode == "near" and distance <= threshold:
            return True
        elif mode == "far" and distance <= threshold:
            return False
    return mode == "far"

def ground_time(df_flight, df_apron, runway_lines, callsign_nr):
    """
    Computes runway time and taxi time for a given flight based on apron and runway transitions.

    Parameters:
        df_flight: DataFrame containing full trajectory data
        df_apron: DataFrame with apron node coordinates (way_id, latitude, longitude)
        runway_lines: List of shapely LineString geometries for runways
        callsign_nr: The callsign group number to evaluate

    Returns:
        Tuple: (runway_time [seconds], taxi_time [seconds])
    """

    # Filter only ground points for the selected flight and sort by time
    flight = df_flight[(df_flight['callsign_group'] == callsign_nr) & (df_flight['onground'] == True)].copy()
    flight = flight.sort_values('timestamp').reset_index(drop=True)

    if flight.empty:
        return None, None, None, None, None

    # Classify the flight as Arrival or Departure
    flight_type = classify_flight(df_flight, callsign_nr, df_apron)

    # ARRIVAL logic
    if flight_type == "Arrival":
        apron_entry_idx = None
        runway_exit_idx = None
        
        # Find the runway used (nearest to the first on-ground point)
        touchdown_point = Point(flight.iloc[0]['longitude'], flight.iloc[0]['latitude'])
        used_runway = None
        min_dist = float('inf')
        for rwy_id, line in enumerate(runway_lines):
            dist = touchdown_point.distance(line) * 111139
            if dist < min_dist:
                min_dist = dist
                used_runway = rwy_id + 1

        # Find the first point inside any apron (end of taxiing)
        for i, row in flight.iterrows():
            if find_apron(row['latitude'], row['longitude'], df_apron) is not None:
                apron_entry_idx = i
                break

        # Find the last point still close to the runway (end of runway phase)
        for i in reversed(range(len(flight))):
            if runway_condition(flight.iloc[i]['latitude'], flight.iloc[i]['longitude'], runway_lines, mode="near"):
                runway_exit_idx = i
                break

        if apron_entry_idx is None or runway_exit_idx is None or apron_entry_idx <= runway_exit_idx:
            return None, None, None, None, None

        runway_time = (pd.to_datetime(flight.iloc[runway_exit_idx]['timestamp']) - pd.to_datetime(flight.iloc[0]['timestamp'])).total_seconds()
        taxi_time = (pd.to_datetime(flight.iloc[apron_entry_idx]['timestamp']) - pd.to_datetime(flight.iloc[runway_exit_idx]['timestamp'])).total_seconds()
        t_start = pd.to_datetime(flight.iloc[0]['timestamp'])
        t_end = pd.to_datetime(flight.iloc[runway_exit_idx]['timestamp'])
        
        return runway_time, taxi_time, used_runway, t_start, t_end

    # DEPARTURE logic
    elif flight_type == "Departure":
        apron_exit_idx = None
        runway_entry_idx = None
        
        # Find the runway used (nearest to the last on-ground point)
        takeoff_point = Point(flight.iloc[-1]['longitude'], flight.iloc[-1]['latitude'])
        used_runway = None
        min_dist = float('inf')
        for rwy_id, line in enumerate(runway_lines):
            dist = takeoff_point.distance(line) * 111139
            if dist < min_dist:
                min_dist = dist
                used_runway = rwy_id + 1


        # Find the first point that is no longer inside any apron (apron exit)
        for i, row in enumerate(flight.itertuples()):
            if find_apron(row.latitude, row.longitude, df_apron) is None:
                apron_exit_idx = i
                break

        # From that point on, find the first point that is near a runway (runway entry)
        if apron_exit_idx is not None:
            for i in range(apron_exit_idx + 1, len(flight)):
                if runway_condition(flight.iloc[i]['latitude'], flight.iloc[i]['longitude'], runway_lines, mode="near"):
                    runway_entry_idx = i
                    break

        if apron_exit_idx is None or runway_entry_idx is None or runway_entry_idx <= apron_exit_idx:
            return None, None, None, None, None

        taxi_time = (pd.to_datetime(flight.iloc[runway_entry_idx]['timestamp']) - pd.to_datetime(flight.iloc[apron_exit_idx]['timestamp'])).total_seconds()
        runway_time = (pd.to_datetime(flight.iloc[-1]['timestamp']) - pd.to_datetime(flight.iloc[runway_entry_idx]['timestamp'])).total_seconds()
        t_start = pd.to_datetime(flight.iloc[runway_entry_idx]['timestamp'])
        t_end = pd.to_datetime(flight.iloc[-1]['timestamp'])
        
        return runway_time, taxi_time, used_runway, t_start, t_end

    return None, None, None, None, None

