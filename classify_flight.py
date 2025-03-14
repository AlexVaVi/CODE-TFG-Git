import math
import pandas as pd

def classify_flight(trajectory_df, callsign_nr, runway_nodes_df, threshold=500):

    trajectory_df = trajectory_df[(trajectory_df['callsign_group'] == callsign_nr)]
    
    # Función interna para calcular la distancia entre dos puntos usando Haversine
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371000  # Radio de la Tierra en metros
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
    
    # Extraer el primer y último punto de la trayectoria
    first_point = trajectory_df.iloc[0]
    last_point  = trajectory_df.iloc[-1]
    
    # Calcular la distancia mínima desde el primer punto a cualquiera de los nodos
    distances_first = runway_nodes_df.apply(
        lambda row: haversine(first_point['latitude'], first_point['longitude'],
                              row['latitude'], row['longitude']),
        axis=1
    )
    min_distance_first = distances_first.min()
    
    # Calcular la distancia mínima desde el último punto a cualquiera de los nodos
    distances_last = runway_nodes_df.apply(
        lambda row: haversine(last_point['latitude'], last_point['longitude'],
                              row['latitude'], row['longitude']),
        axis=1
    )
    min_distance_last = distances_last.min()
    
    # # Distances
    # print("Distance first point:", min_distance_first, "meters")
    # print("Distancia last point:", min_distance_last, "meters")
    
    # Clasificación usando la heurística:
    if min_distance_last < threshold and min_distance_last < min_distance_first:
        return "Departure"
    elif min_distance_first < threshold and min_distance_first < min_distance_last:
        return "Arrival"
    else:
        return "Unknown"
