import folium
import pandas as pd
import branca.colormap as cm
import numpy as np

file_path = r'C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\CODE TFG\all_lat_lon_2024_10_01_buf.csv'
df = pd.read_csv(file_path, delimiter=';')

# print("Flights:", df['callsign'].unique())

callsign = df['callsign'].unique()[1]  
df_flight = df[(df['callsign'] == callsign)]
num_points = len(df_flight)

df_flight['latitude'] = df['latitude'].str.replace(',', '.').astype(float)
df_flight['longitude'] = df['longitude'].str.replace(',', '.').astype(float)

df_flight['date'] = pd.to_datetime(df_flight['date'], format="%d/%m/%Y")
df_flight['timestamp_clean'] = df_flight['timestamp'].str.replace("+00:00", "", regex=False)
df_flight['datetime'] = pd.to_datetime(df_flight['date'].astype(str) + ' ' + df_flight['timestamp_clean'], format="%Y-%m-%d %H:%M:%S")

first_time = df_flight['datetime'].iloc[0]
last_time = df_flight['datetime'].iloc[-1]
elapsed_time = last_time - first_time
elapsed_time_seconds = elapsed_time.total_seconds()
hours = int(elapsed_time_seconds // 3600)
minutes = int((elapsed_time_seconds % 3600) // 60)
seconds = int((elapsed_time_seconds % 3600) % 60)
formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

center_lat = df_flight['latitude'].mean()
center_lon = df_flight['longitude'].mean()

m = folium.Map(location=[center_lat, center_lon], zoom_start=16)

num_bins = 10
lat_bins = np.linspace(df_flight['latitude'].min(), df_flight['latitude'].max(), num_bins)
lon_bins = np.linspace(df_flight['longitude'].min(), df_flight['longitude'].max(), num_bins)

df_flight['lat_bin'] = np.digitize(df_flight['latitude'], lat_bins)
df_flight['lon_bin'] = np.digitize(df_flight['longitude'], lon_bins)

density_map = df_flight.groupby(['lat_bin', 'lon_bin']).size().reset_index(name='density')

min_density, max_density = density_map['density'].min(), density_map['density'].max()
colormap = cm.LinearColormap(colors=['blue','green','yellow','red'], vmin=min_density, vmax=max_density)

for i in range(1, len(df_flight)):
    lat_bin, lon_bin = df_flight.iloc[i]['lat_bin'], df_flight.iloc[i]['lon_bin']
    density_value = density_map[(density_map['lat_bin'] == lat_bin) & (density_map['lon_bin'] == lon_bin)]['density'].values[0]

    folium.PolyLine(
        locations=[(df_flight.iloc[i-1]['latitude'], df_flight.iloc[i-1]['longitude']),
                   (df_flight.iloc[i]['latitude'], df_flight.iloc[i]['longitude'])],
        color=colormap(density_value),
        weight=4,
        opacity=0.8
    ).add_to(m)
    
html = f"""
<div style="position: fixed;
            top: 10px; left: 10px; width: 250px; height: 40px;
            background-color: white; z-index:9999; font-size:14px;
            padding: 5px; border-radius:5px; box-shadow:2px 2px 6px rgba(0,0,0,0.5);">
    Ground time for {callsign}: {formatted_time}
</div>
"""
m.get_root().html.add_child(folium.Element(html))

colormap.caption = "Density heatmap"
colormap.add_to(m)
m.save("heatmap_density.html")  

print(f"Number of points for flight {callsign}: {num_points}")
print(f"Ground time spent for {callsign}: {elapsed_time}")
print(f"Map succesfully saved as 'heatmap_density.html'")
