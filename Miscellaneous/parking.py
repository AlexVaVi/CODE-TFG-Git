import requests
import folium
from shapely.geometry import LineString
import numpy as np
import webbrowser
import csv

# === Step 1: Define Overpass API query to retrieve Arlanda parking positions ===
overpass_url = "http://overpass-api.de/api/interpreter"
overpass_query = """
[out:json];
area[name="Stockholm-Arlanda flygplats"]->.a;
(
  way(area.a)["aeroway"="parking_position"];    
  node(w);
);
out body;
"""

# === Step 2: Send request to Overpass API ===
response = requests.get(overpass_url, params={'data': overpass_query})
data = response.json()

# === Step 3: Extract all nodes and store by ID ===
nodes = {}
for element in data['elements']:
    if element['type'] == 'node':
        nodes[element['id']] = (element['lat'], element['lon'])

# === Step 4: Extract parkings (ways with node references) ===
parkings = []
for element in data['elements']:
    if element['type'] == 'way' and 'nodes' in element:
        coords = [nodes[node_id] for node_id in element['nodes'] if node_id in nodes]
        if coords:  # Only keep if nodes were found
            parkings.append(coords)

# === Step 5: Basic validation ===
if parkings:
    print(f"Total parking positions found: {len(parkings)}")
else:
    print("No parking positions found.")

# === Step 6: Create interactive map centered at Arlanda ===
center_lat = np.mean([coord[0] for p in parkings for coord in p])
center_lon = np.mean([coord[1] for p in parkings for coord in p])
m = folium.Map(location=[center_lat, center_lon], zoom_start=13)
folium.TileLayer('CartoDB Positron').add_to(m)

# === Step 7: Draw each parking path as a polyline and annotate with index ===
for idx, parking in enumerate(parkings):
    folium.PolyLine(locations=parking, color='#333333', weight=2.5, opacity=1).add_to(m)

    # Place a marker at the midpoint of the parking path
    mid_idx = len(parking) // 2
    mid_lat, mid_lon = parking[mid_idx]

    folium.Marker(
        location=[mid_lat, mid_lon],
        icon=folium.DivIcon(
            html=f'''
            <div style="
                font-size: 12px;
                font-weight: bold;
                color: black;
                background-color: white;
                padding: 2px 4px;
                border-radius: 4px;
                text-align: center;
            ">
                {idx}
            </div>
            '''
        )
    ).add_to(m)

# === Step 8: Add a legend to the map ===
legend_html = '''
    <div style="position: fixed; 
                top: 200px; left: 200px; width: 90px; height: 50px; 
                background-color: white; z-index:9999; font-size:14px; 
                padding: 5px; border-radius:5px; box-shadow:2px 2px 6px rgba(0,0,0,0.5);">
        <span style="background-color: #333333; border-radius: 50%; width: 15px; height: 15px; display: inline-block; margin-right: 5px;"></span> Parking positions <br>
    </div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# === Step 9: Save and open the map ===
m.save('arlanda_parkings_map.html')
print("Map successfully saved as 'arlanda_parkings_map.html'")
webbrowser.open('arlanda_parkings_map.html')

# === Step 10: Save node-wise CSV with way-node mapping ===
with open('arlanda_parking_nodes_by_way.csv', mode='w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Way ID', 'Node ID', 'Latitude', 'Longitude'])  # CSV header

    for element in data['elements']:
        if element['type'] == 'way' and 'nodes' in element:
            way_id = element['id']
            for node_id in element['nodes']:
                if node_id in nodes:
                    lat, lon = nodes[node_id]
                    writer.writerow([way_id, node_id, lat, lon])

print("CSV file 'arlanda_parking_nodes_by_way.csv' successfully saved.")
