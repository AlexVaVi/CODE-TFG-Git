import requests
import folium
from shapely.geometry import LineString
import numpy as np
import webbrowser

# === 1. Download RUNWAYS ===
# Define Overpass API query to retrieve runways in Arlanda
overpass_url = "http://overpass-api.de/api/interpreter"
overpass_query = """
[out:json];
area[name="Stockholm-Arlanda flygplats"]->.a;
(
  way(area.a)["aeroway"="runway"];
  node(w);
);
out body;
"""

# Request data from Overpass API
response = requests.get(overpass_url, params={'data': overpass_query})
data = response.json()

# Extract node coordinates
nodes = {}
for element in data['elements']:
    if element['type'] == 'node':
        nodes[element['id']] = (element['lat'], element['lon'])

# Match ways (runways) to node coordinates
runways = []
for element in data['elements']:
    if element['type'] == 'way' and 'nodes' in element:
        coords = [nodes[node_id] for node_id in element['nodes'] if node_id in nodes]
        if coords:
            runways.append(coords)

print(f"✅ Found {len(runways)} runways" if runways else "⚠️ No runways found")

# === 2. Setup map centered on Arlanda ===
center_lat = np.mean([pt[0] for rwy in runways for pt in rwy])
center_lon = np.mean([pt[1] for rwy in runways for pt in rwy])
m = folium.Map(location=[center_lat, center_lon], zoom_start=13)
folium.TileLayer('CartoDB Positron').add_to(m)

# Add runways to map with marker labels
for idx, runway in enumerate(runways, start=1):
    folium.PolyLine(locations=runway, color='#333333', weight=2.5, opacity=1).add_to(m)
    mid_lat = np.mean([pt[0] for pt in runway])
    mid_lon = np.mean([pt[1] for pt in runway])
    folium.Marker(
        [mid_lat, mid_lon],
        icon=folium.DivIcon(html=f'<div style="font-size:12px; color:#333;"><b>RWY {idx}</b></div>')
    ).add_to(m)

# === 3. Download TAXIWAYS ===
overpass_query = """
[out:json];
area[name="Stockholm-Arlanda flygplats"]->.a;
(
  way(area.a)["aeroway"="taxiway"];
  node(w);
);
out body;
"""
response = requests.get(overpass_url, params={'data': overpass_query})
data = response.json()

# Extract node coordinates
nodes = {}
for element in data['elements']:
    if element['type'] == 'node':
        nodes[element['id']] = (element['lat'], element['lon'])

# Match ways (taxiways) to node coordinates
taxiways = []
for element in data['elements']:
    if element['type'] == 'way' and 'nodes' in element:
        coords = [nodes[node_id] for node_id in element['nodes'] if node_id in nodes]
        if coords:
            taxiways.append(coords)

print(f"✅ Found {len(taxiways)} taxiways" if taxiways else "⚠️ No taxiways found")

# Plot taxiways on map
for taxiway in taxiways:
    folium.PolyLine(locations=taxiway, color='#4b6eaf', weight=2.5, opacity=1).add_to(m)

# === 4. Download APRONS ===
overpass_query = """
[out:json];
area[name="Stockholm-Arlanda flygplats"]->.a;
(
  way(area.a)["aeroway"="apron"];
  node(w);
);
out body;
"""
response = requests.get(overpass_url, params={'data': overpass_query})
data = response.json()

# Extract node coordinates
nodes = {}
for element in data['elements']:
    if element['type'] == 'node':
        nodes[element['id']] = (element['lat'], element['lon'])

# Match ways (aprons) to node coordinates
aprons = []
for element in data['elements']:
    if element['type'] == 'way' and 'nodes' in element:
        coords = [nodes[node_id] for node_id in element['nodes'] if node_id in nodes]
        if coords:
            aprons.append(coords)

print(f"✅ Found {len(aprons)} aprons" if aprons else "⚠️ No aprons found")

# Plot aprons on map with labels
for idx, apron in enumerate(aprons, start=1):
    folium.PolyLine(locations=apron, color='#bbbbbb', weight=2.5, opacity=1).add_to(m)
    mid_lat = np.mean([pt[0] for pt in apron])
    mid_lon = np.mean([pt[1] for pt in apron])
    folium.Marker(
        [mid_lat, mid_lon],
        icon=folium.DivIcon(html=f'<div style="font-size:12px; color:#444;"><b>AP {idx}</b></div>')
    ).add_to(m)

# === 5. Add legend ===
legend_html = '''
    <div style="position: fixed; 
                top: 200px; left: 200px; width: 110px; height: 70px; 
                background-color: white; z-index:9999; font-size:14px; 
                padding: 5px; border-radius:5px; box-shadow:2px 2px 6px rgba(0,0,0,0.5);">
        <span style="background-color: #333333; border-radius: 50%; width: 15px; height: 15px; display: inline-block; margin-right: 5px;"></span> Runways<br>
        <span style="background-color: #4b6eaf; border-radius: 50%; width: 15px; height: 15px; display: inline-block; margin-right: 5px;"></span> Taxiways<br>
        <span style="background-color: #bbbbbb; border-radius: 50%; width: 15px; height: 15px; display: inline-block; margin-right: 5px;"></span> Aprons
    </div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# === 6. Save map and open it ===
m.save('arlanda_airport_map.html')
print("✅ Map saved as 'arlanda_airport_map.html'")
webbrowser.open('arlanda_airport_map.html')
