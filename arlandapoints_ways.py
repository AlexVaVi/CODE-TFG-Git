import requests
import pandas as pd

def get_airport_nodes(aeroway_type):
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    area["name"="Stockholm-Arlanda flygplats"]->.a;
    (
      way(area.a)["aeroway"="{aeroway_type}"];
      node(w);
    );
    out body;
    """

    response = requests.get(overpass_url, params={'data': overpass_query})
    data = response.json()

    nodes_dict = {}
    for element in data['elements']:
        if element['type'] == 'node':
            nodes_dict[element['id']] = {'lat': element['lat'], 'lon': element['lon']}

    elements = []  # Ahora sí está correctamente definida
    for element in data['elements']:
        if element['type'] == 'way':
            way_id = element['id']
            for node_id in element['nodes']:
                if node_id in nodes_dict:
                    node_data = nodes_dict[node_id]
                    node_element = {
                        'way_id': way_id,
                        'node_id': node_id,
                        'type': aeroway_type,
                        'latitude': node_data['lat'],
                        'longitude': node_data['lon']
                    }
                    elements.append(node_element)

    return elements

# Obtener nodos
runway_nodes = get_airport_nodes("runway")
taxiway_nodes = get_airport_nodes("taxiway")
apron_nodes = get_airport_nodes("apron")

# Crear DataFrame
df = pd.DataFrame(runway_nodes + taxiway_nodes + apron_nodes)

# Guardar en CSV
df.to_csv('arlanda_nodes_ways.csv', index=False)

print(f"Saved {len(df)} nodes to arlanda_airport_nodes.csv")
