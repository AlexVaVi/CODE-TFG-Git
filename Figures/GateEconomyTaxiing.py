import folium
from shapely.geometry import LineString

# Approximate coordinates to center the map on Stockholm Arlanda Airport (ESSA)
map_center = [59.6519, 17.9238]
airport_map = folium.Map(location=map_center, zoom_start=14, tiles='CartoDB positron')

# === 1. Draw RUNWAYS (black lines) ===
for rwy_id in df_airport['way_id'].unique():
    rwy_points = df_airport[df_airport['way_id'] == rwy_id].sort_values(by='node_id')
    coords = list(zip(rwy_points['latitude'], rwy_points['longitude']))
    if len(coords) >= 2:
        folium.PolyLine(coords, color='black', weight=4, opacity=1).add_to(airport_map)

# === 2. Draw APRON 13 (dark blue line) ===
apron_13 = df_parkings[df_parkings['Apron'] == 13].sort_values(by='Node ID')
coords_apron13 = list(zip(apron_13['Latitude'], apron_13['Longitude']))
if coords_apron13:
    folium.PolyLine(coords_apron13, color='darkblue', weight=4, opacity=0.9).add_to(airport_map)

# === 3. Plot specific flight paths (red lines) ===
for callsign_nr in [115, 211]:
    path_df = fp.flight_path(df_flight, callsign_nr, df_apron)  # Should return a DataFrame with 'Latitude' and 'Longitude'
    coords_path = list(zip(path_df['Latitude'], path_df['Longitude']))
    if coords_path:
        folium.PolyLine(
            coords_path,
            color='red',
            weight=3,
            opacity=0.8,
            tooltip=f'Callsign {callsign_nr}'
        ).add_to(airport_map)

# === Save the interactive map ===
airport_map.save("arlanda_map.html")
