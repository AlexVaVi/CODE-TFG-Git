import pandas as pd
import numpy as np
import folium
from shapely.geometry import Point
from sklearn.preprocessing import MinMaxScaler
import matplotlib.cm as cm

def hotspots2(df, start_time=None, end_time=None, grid_size=0.00005, min_points=5):
    """
    Calculates hotspot levels in a grid-based method.
    """
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(by='timestamp')

    # Filter by time range
    df = df[(df['timestamp'] >= start_time) & (df['timestamp'] <= end_time)]
    df = df.dropna(subset=['latitude', 'longitude', 'callsign', 'callsign_group']).copy()

    # Define grid cells
    df['lat_bin'] = (df['latitude'] // grid_size) * grid_size
    df['lon_bin'] = (df['longitude'] // grid_size) * grid_size
    df['grid_id'] = df['lat_bin'].astype(str) + '_' + df['lon_bin'].astype(str)

    # Group by grid cell
    hotspot_data = []

    for grid_id, group in df.groupby('grid_id'):
        total_points = len(group)
        unique_callsigns = group['callsign'].nunique()
        callsign_counts = group.groupby('callsign').size()
        max_points_per_callsign = callsign_counts.max()

        if total_points >= min_points:
            # Assign level based on thresholds
            if total_points >= 45 and unique_callsigns >= 5:
                level = 5
            elif total_points >= 35 and unique_callsigns >= 3:
                level = 4
            elif total_points >= 25 and unique_callsigns >= 2:
                level = 3
            elif total_points >= 15 and unique_callsigns == 1:
                level = 2
            elif total_points < 15 and unique_callsigns == 1:
                level = 1
            else:
                level = 0

            hotspot_data.append({
                'grid_id': grid_id,
                'lat': group['lat_bin'].iloc[0] + grid_size / 2,
                'lon': group['lon_bin'].iloc[0] + grid_size / 2,
                'total_points': total_points,
                'unique_callsigns': unique_callsigns,
                'level': level
            })

    return pd.DataFrame(hotspot_data)

def visualize_hotspots2(hotspots_df, map_filename='grid_hotspots_map.html'):
    """
    Visualizes grid hotspot levels on a Folium map.
    """
    if hotspots_df.empty:
        print("✅ No hotspots to visualize.")
        return

    fmap = folium.Map(location=[hotspots_df['lat'].mean(), hotspots_df['lon'].mean()], zoom_start=15)
    colormap = cm.get_cmap('Reds', 6)  # 0 to 5 levels

    for _, row in hotspots_df.iterrows():
        color = colormap(row['level'] / 5)
        color_hex = '#%02x%02x%02x' % tuple(int(255 * c) for c in color[:3])

        folium.CircleMarker(
            location=(row['lat'], row['lon']),
            radius=6 + row['level'] * 2,
            color=color_hex,
            fill=True,
            fill_opacity=0.7,
            popup=(
                f"Level: {row['level']}<br>"
                f"Total Points: {row['total_points']}<br>"
                f"Unique Callsigns: {row['unique_callsigns']}"
            )
        ).add_to(fmap)

    fmap.save(map_filename)
    print(f"✅ Grid hotspot map saved to {map_filename}")