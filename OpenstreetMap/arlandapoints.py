import requests
import pandas as pd
import folium
import numpy as np

def get_geodata_from_overpass(aeroway_type):
    """
    Retrieves geographical data (runways, taxiways, aprons) from Overpass API 
    for Stockholm-Arlanda airport based on the specified 'aeroway' type.
    
    Parameters:
        aeroway_type (str): Type of aeroway ('runway', 'taxiway', or 'apron')
    
    Returns:
        list of lists of coordinates (lat, lon) for each element found
    """
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    # Define Overpass QL query for the given aeroway type
    overpass_query = f"""
    [out:json];
    area[name="Stockholm-Arlanda flygplats"]->.a;
    (
      way(area.a)["aeroway"="{aeroway_type}"];
      node(w);
    );
    out body;
    """
    
    # Send request and parse response
    response = requests.get(overpass_url, params={'data': overpass_query})
    data = response.json()

    # Extract node coordinates
    nodes = {}
    for element in data['elements']:
        if element['type'] == 'node':
            nodes[element['id']] = (element['lat'], element['lon'])
    
    # Map each 'way' to its corresponding list of node coordinates
    elements = []
    for element in data['elements']:
        if element['type'] == 'way' and 'nodes' in element:
            coords = [nodes[node_id] for node_id in element['nodes'] if node_id in nodes]
            if coords:
                elements.append(coords)
    
    return elements

# === Retrieve and count airport features ===
runways = get_geodata_from_overpass("runway")
taxiways = get_geodata_from_overpass("taxiway")
aprons = get_geodata_from_overpass("apron")

print(f"✅ Found {len(runways)} runways")
print(f"✅ Found {len(taxiways)} taxiways")
print(f"✅ Found {len(aprons)} aprons")

# === Flatten all nodes into a DataFrame with labels ===
data = []

for route in runways:
    for lat, lon in route:
        data.append({'type': 'runway', 'latitude': lat, 'longitude': lon})

for route in taxiways:
    for lat, lon in route:
        data.append({'type': 'taxiway', 'latitude': lat, 'longitude': lon})

for route in aprons:
    for lat, lon in route:
        data.append({'type': 'apron', 'latitude': lat, 'longitude': lon})

df = pd.DataFrame(data)

# === Save nodes to CSV file ===
df.to_csv('arlanda_airport_nodes.csv', index=False)
print("📄 Coordinates saved to 'arlanda_airport_nodes.csv'")
