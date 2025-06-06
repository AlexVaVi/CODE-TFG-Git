# distance_to_infra.py
import numpy as np
import pandas as pd
from conversion import latlon_to_xy

def distance_to_infra(x_est, y_est, ref_lat, ref_lon):
    file_path = r'C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\arlanda_airport_nodes.csv'
    df = pd.read_csv(file_path, delimiter=',')
    
    df_taxiway = df[df['type'] == 'taxiway'].copy()
    df_runway = df[df['type'] == 'runway'].copy()
    
    taxi_lat = df_taxiway['latitude'].values
    taxi_lon = df_taxiway['longitude'].values
    taxi_x, taxi_y = latlon_to_xy(taxi_lat, taxi_lon, ref_lat, ref_lon)
    
    runway_lat = df_runway['latitude'].values
    runway_lon = df_runway['longitude'].values
    runway_x, runway_y = latlon_to_xy(runway_lat, runway_lon, ref_lat, ref_lon)
    
    taxi_distances = []
    for tx, ty in zip(taxi_x, taxi_y):
        dx = x_est - tx
        dy = y_est - ty
        dist = np.sqrt(dx**2 + dy**2)
        taxi_distances.append((dist, dx, dy))
    taxi_min = min(taxi_distances, key=lambda t: t[0]) if taxi_distances else (np.inf, 0, 0)
    
    runway_distances = []
    for rx, ry in zip(runway_x, runway_y):
        dx = x_est - rx
        dy = y_est - ry
        dist = np.sqrt(dx**2 + dy**2)
        runway_distances.append((dist, dx, dy))
    runway_min = min(runway_distances, key=lambda t: t[0]) if runway_distances else (np.inf, 0, 0)
    
    if taxi_min[0] <= runway_min[0]:
        infra_type = 'taxiway'
        min_distance, dx, dy = taxi_min
    else:
        infra_type = 'runway'
        min_distance, dx, dy = runway_min
        
    if min_distance != 0:
        dphi_dx = dx / min_distance
        dphi_dy = dy / min_distance
    else:
        dphi_dx = dphi_dy = 0
    return infra_type, min_distance, dphi_dx, dphi_dy
