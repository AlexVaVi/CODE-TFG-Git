import requests
import pandas as pd
import folium
import numpy as np

def get_geodata_from_overpass(aeroway_type):
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    area[name="Stockholm-Arlanda flygplats"]->.a;
    (
      way(area.a)["aeroway"="{aeroway_type}"];
      node(w);
    );
    out body;
    """
    
    response = requests.get(overpass_url, params={'data': overpass_query})
    data = response.json()

    # Extraer los nodos
    nodes = {}
    for element in data['elements']:
        if element['type'] == 'node':
            nodes[element['id']] = (element['lat'], element['lon'])
    
    # Extraer las rutas (ways) y asociarlas con los nodos
    elements = []
    for element in data['elements']:
        if element['type'] == 'way' and 'nodes' in element:
            coords = []
            for node_id in element['nodes']:
                if node_id in nodes:
                    coords.append(nodes[node_id])  # Asociar la coordenada de cada nodo al elemento
            if coords:  # Solo añadir la ruta si tiene nodos asociados
                elements.append(coords)
    
    return elements

# Obtener runways, taxiways y aprons
runways = get_geodata_from_overpass("runway")
taxiways = get_geodata_from_overpass("taxiway")
aprons = get_geodata_from_overpass("apron")

print(f"Total de runways encontrados: {len(runways)}")
print(f"Total de taxiways encontrados: {len(taxiways)}")
print(f"Total de aprons encontrados: {len(aprons)}")

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

df.to_csv('arlanda_airport_nodes.csv', index=False)

print("Puntos guardados en 'arlanda_airport_nodes.csv'")