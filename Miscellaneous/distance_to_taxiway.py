# distance_to_taxiway.py
import numpy as np
import pandas as pd
from conversion import latlon_to_xy

def distance_to_taxiway(x_est, y_est, ref_lat, ref_lon):
    """
    Computes the distance from a given point (x_est, y_est) to the closest taxiway node.
    The taxiway node coordinates are read from a CSV file in latitude/longitude format.

    Args:
        x_est (float): X-coordinate (meters) of the estimated point.
        y_est (float): Y-coordinate (meters) of the estimated point.
        ref_lat (float): Reference latitude used for coordinate conversion.
        ref_lon (float): Reference longitude used for coordinate conversion.

    Returns:
        tuple: (min_distance, dphi_dx, dphi_dy)
            - min_distance (float): Minimum distance to the nearest taxiway node (in meters).
            - dphi_dx (float): Partial derivative of distance with respect to x.
            - dphi_dy (float): Partial derivative of distance with respect to y.
    """
    
    # === Load airport nodes CSV ===
    file_path = r'C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\CODE TFG\arlanda_airport_nodes.csv'
    df = pd.read_csv(file_path, delimiter=';')

    # === Filter only taxiway points ===
    df_taxiway = df[df['type'] == 'taxiway'].copy()

    # === Convert lat/lon to float (comma to dot for locales) ===
    df_taxiway['latitude'] = df_taxiway['latitude'].str.replace(',', '.').astype(float)
    df_taxiway['longitude'] = df_taxiway['longitude'].str.replace(',', '.').astype(float)

    # === Convert coordinates to local XY frame ===
    taxi_lat = df_taxiway['latitude'].values
    taxi_lon = df_taxiway['longitude'].values
    taxi_x, taxi_y = latlon_to_xy(taxi_lat, taxi_lon, ref_lat, ref_lon)

    # === Compute distance to all taxiway nodes ===
    distances = []
    for tx, ty in zip(taxi_x, taxi_y):
        dx = x_est - tx
        dy = y_est - ty
        dist = np.sqrt(dx**2 + dy**2)
        distances.append((dist, dx, dy))

    # === Find the nearest taxiway point ===
    min_distance, min_dx, min_dy = min(distances, key=lambda x: x[0])

    # === Compute partial derivatives if not zero distance ===
    if min_distance != 0:
        dphi_dx = min_dx / min_distance
        dphi_dy = min_dy / min_distance
    else:
        dphi_dx = dphi_dy = 0

    return min_distance, dphi_dx, dphi_dy

