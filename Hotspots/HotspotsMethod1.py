import pandas as pd
from shapely.geometry import Point, LineString
import folium
from shapely.ops import nearest_points
import numpy as np
from sklearn.neighbors import BallTree
from geopy.distance import geodesic

#HOTSPOTS

def hotspots1(df, runway_lines, start_time=None, end_time=None, max_distance=30, time_interval='60s', exclusion_buffer=10):
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(by='timestamp')

    # Filter by time range
    df = df[(df['timestamp'] >= start_time) & (df['timestamp'] <= end_time)]

    # Assign rounded time groups
    df['time_group'] = df['timestamp'].dt.floor(time_interval)

    # Exclude points near runway lines
    def is_near_runway(lat, lon, runway_lines, buffer_m=10):
        point = Point(lon, lat)
        for rwy in runway_lines:
            nearest_point = nearest_points(rwy, point)[0]
            distance = geodesic((point.y, point.x), (nearest_point.y, nearest_point.x)).meters
            if distance <= buffer_m:
                return True
        return False

    df['near_runway'] = df.apply(lambda row: is_near_runway(row['latitude'], row['longitude'], runway_lines), axis=1)
    df_filtered = df[~df['near_runway']].copy()

    # Final hot spot detection
    earth_radius = 6371000
    hot_spots = []

    for _, group in df_filtered.groupby('time_group'):
        group = group.dropna(subset=['latitude', 'longitude'])

        if len(group) < 2:
            continue

        coords = np.deg2rad(group[['latitude', 'longitude']].values)
        tree = BallTree(coords, metric='haversine')
        indices = tree.query_radius(coords, r=max_distance / earth_radius)

        for i, neighbors in enumerate(indices):
            for j in neighbors:
                if i < j:
                    a = group.iloc[i]
                    b = group.iloc[j]

                    # Ignore same aircraft trajectory
                    if a['callsign_group'] == b['callsign_group']:
                        continue

                    # Calculate actual distance (for precision)
                    dist = geodesic((a['latitude'], a['longitude']), (b['latitude'], b['longitude'])).meters
                    if dist <= max_distance:
                        hot_spots.append({
                            'timestamp': a['timestamp'],
                            'callsign_1': a['callsign'], 'callsign_2': b['callsign'],
                            'lat1': a['latitude'], 'lon1': a['longitude'],
                            'lat2': b['latitude'], 'lon2': b['longitude'],
                            'distance_m': round(dist, 1)
                        })

    df_hotspots = pd.DataFrame(hot_spots)
    df_hotspots['minute'] = df_hotspots['timestamp'].dt.floor('1min')
    df_hotspots = df_hotspots.drop_duplicates(subset=['callsign_1', 'callsign_2', 'minute'])

    return df_hotspots




 
#VISUALIZATION

def visualize_hotspots1(hot_spots_df, map_filename='hotspots_map.html'):
    """
    Generate a folium map with hot spot circles at midpoint locations.
    """
    import folium

    if hot_spots_df.empty:
        print("✅ No hot spots to visualize.")
        return

    center_lat = hot_spots_df[['lat1', 'lat2']].mean().mean()
    center_lon = hot_spots_df[['lon1', 'lon2']].mean().mean()
    fmap = folium.Map(location=[center_lat, center_lon], zoom_start=15)
    folium.TileLayer('CartoDB Positron').add_to(fmap)

    for _, row in hot_spots_df.iterrows():
        # Draw line between aircraft (optional, for visual aid)
        # folium.PolyLine([(row['lat1'], row['lon1']), (row['lat2'], row['lon2'])],
        #                 color='orange', weight=2).add_to(fmap)

        # Calculate midpoint
        mid_lat = (row['lat1'] + row['lat2']) / 2
        mid_lon = (row['lon1'] + row['lon2']) / 2

        # Add red circle at midpoint
        folium.CircleMarker(
            location=[mid_lat, mid_lon],
            radius=6,
            color='red',
            fill=True,
            fill_color='red',
            fill_opacity=0.8,
            popup=f"Hot spot ({row['distance_m']} m at {row['timestamp']} between {row['callsign_1']} and {row['callsign_2']})",
        ).add_to(fmap)

    fmap.save(map_filename)
    print(f"✅ Hot spot map saved to {map_filename}")