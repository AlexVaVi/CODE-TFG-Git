from shapely.geometry import Point, Polygon

def find_apron(lat, lon, df_apron_nodes):
    
    point = Point(lon, lat)
    unique_ids = df_apron_nodes['way_id'].unique()

    for i, node_id in enumerate(unique_ids, start=1):  # Iterate through each unique apron zone
        apron_coords = df_apron_nodes[df_apron_nodes['way_id'] == node_id]
        polygon = Polygon(zip(apron_coords['longitude'], apron_coords['latitude']))  # Create polygon for the apron
        if polygon.contains(point):  # Check if point lies inside this polygon
            return i  # Return apron number based on order

    return None  # Return None if the point does not belong to any apron zone
