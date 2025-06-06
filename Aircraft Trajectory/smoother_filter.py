# kalman_filter.py

import numpy as np
import folium
import webbrowser
from shapely.geometry import Point, LineString
from conversion import latlon_to_xy, xy_to_latlon
from distance_to_infra import distance_to_infra
import pandas as pd
from ApronAnalysis import find_apron

def smoother_filter(df_flight, ref_lat, ref_lon):
    """
    Applies a position smoothing algorithm using a constrained projection filter,
    snapping positions to known infrastructure segments if outside apron areas.

    Parameters:
      df_flight: DataFrame containing flight trajectory (with latitude, longitude, groundspeed, and track).
      ref_lat, ref_lon: reference coordinates for conversion to and from metric (XY) system.

    Returns:
      corrected_lat: array of smoothed latitude values.
      corrected_lon: array of smoothed longitude values.
      closest_segments: list of infrastructure segments used for projection.
    """

    # Load apron geometry and filter to only include apron areas
    df_apron = pd.read_csv(r'C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\arlanda_airport_nodes.csv')
    df_apron = df_apron[df_apron['type'] == 'apron']

    # Load airport infrastructure nodes and convert to metric coordinates
    df = pd.read_csv(r'C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\arlanda_airport_nodes.csv')
    callsign = df_flight['callsign'].unique()[0]

    x, y = latlon_to_xy(df["latitude"].values, df["longitude"].values, ref_lat, ref_lon)
    df["x"] = x
    df["y"] = y

    # Build infrastructure segments as LineStrings grouped by type and way_id
    linestrings = {}
    for (way_type, way_id), group in df.groupby(["type", "way_id"]):
        points = [Point(row["x"], row["y"]) for _, row in group.iterrows()]
        if len(points) >= 2:
            linestrings[(way_type, way_id)] = LineString(points)

    # Ensure correct data types
    df_flight['latitude'] = df_flight['latitude'].astype(float)
    df_flight['longitude'] = df_flight['longitude'].astype(float)
    df_flight['groundspeed'] = df_flight['groundspeed'].astype(float)
    df_flight['track'] = np.radians(df_flight['track'].astype(float))

    # Compute velocity components
    vx = df_flight['groundspeed'].values * np.cos(df_flight['track'].values)
    vy = df_flight['groundspeed'].values * np.sin(df_flight['track'].values)

    # Original positions in degrees
    latitudes = df_flight['latitude'].values
    longitudes = df_flight['longitude'].values
    n = len(latitudes)

    # Convert positions to meters
    x, y = latlon_to_xy(latitudes, longitudes, ref_lat, ref_lon)

    # Initialize state vector: [x, y, vx, vy]
    X_estimate = np.zeros((n, 4))
    X_estimate[0] = [x[0], y[0], vx[0], vy[0]]

    # Set threshold for snapping to infrastructure (if not in apron)
    threshold = 50.0

    closest_segments = []
    unique_segments = []
    prev_seg = None

    for k in range(n):
        current_point = Point(x[k], y[k])

        # If point is within apron area, keep original coordinates
        if find_apron(latitudes[k], longitudes[k], df_apron) is not None:
            X_estimate[k] = [x[k], y[k], vx[k], vy[k]]
            continue

        # Otherwise, project the point to the nearest infrastructure segment
        min_distance = float("inf")
        closest_segment = None
        for segment in linestrings.values():
            dist = current_point.distance(segment)
            if dist < min_distance:
                min_distance = dist
                closest_segment = segment

        # Project point onto closest segment
        dist_along_segment = closest_segment.project(current_point)
        closest_point = closest_segment.interpolate(dist_along_segment)

        # Track transitions between segments
        if prev_seg is None or closest_segment != prev_seg:
            closest_segments.append(closest_segment)
            prev_seg = closest_segment

        # Update estimated position with projected point, keep previous velocity
        X_estimate[k] = (closest_point.x, closest_point.y, X_estimate[k][2], X_estimate[k][3])

    # Convert filtered positions back to latitude and longitude
    corrected_lat, corrected_lon = xy_to_latlon(X_estimate[:, 0], X_estimate[:, 1], ref_lat, ref_lon)

    return corrected_lat, corrected_lon, closest_segments

    
