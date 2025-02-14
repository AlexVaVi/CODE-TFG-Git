# distance_to_taxiway.py
import numpy as np
import pandas as pd
from conversion import latlon_to_xy

def distance_to_taxiway(x_est, y_est, ref_lat, ref_lon):
    """
    Calcula la distancia desde el punto (x_est, y_est) en metros a la posición
    más cercana de un taxiway. Se espera que el CSV de taxiways esté en lat/lon.
    
    Retorna:
      (min_distance, dphi_dx, dphi_dy)
    donde dphi_dx y dphi_dy son las derivadas (en relación a x e y).
    """
    file_path = r'C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\CODE TFG\arlanda_airport_nodes.csv'
    df = pd.read_csv(file_path, delimiter=';')
    
    df_taxiway = df[df['type'] == 'taxiway'].copy()
    df_taxiway['latitude'] = df_taxiway['latitude'].str.replace(',', '.').astype(float)
    df_taxiway['longitude'] = df_taxiway['longitude'].str.replace(',', '.').astype(float)
    
    taxi_lat = df_taxiway['latitude'].values
    taxi_lon = df_taxiway['longitude'].values
    taxi_x, taxi_y = latlon_to_xy(taxi_lat, taxi_lon, ref_lat, ref_lon)
    
    distances = []
    for tx, ty in zip(taxi_x, taxi_y):
        dx = x_est - tx
        dy = y_est - ty
        dist = np.sqrt(dx**2 + dy**2)
        distances.append((dist, dx, dy))
    
    min_distance, min_dx, min_dy = min(distances, key=lambda x: x[0])
    if min_distance != 0:
        dphi_dx = min_dx / min_distance
        dphi_dy = min_dy / min_distance
    else:
        dphi_dx = dphi_dy = 0
    return min_distance, dphi_dx, dphi_dy

