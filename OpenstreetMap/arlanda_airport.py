import requests
import folium
from shapely.geometry import LineString
import numpy as np
import webbrowser

# Definir la consulta Overpass API para obtener los runways de Arlanda (nodos y ways)
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

# Hacer la solicitud a la API de Overpass
response = requests.get(overpass_url, params={'data': overpass_query})

# Procesar los datos obtenidos de la API de Overpass
data = response.json()

# Extraer los nodos
nodes = {}
for element in data['elements']:
    if element['type'] == 'node':
        nodes[element['id']] = (element['lat'], element['lon'])

# Extraer los runways (ways) y asociarlos con los nodos
runways = []
for element in data['elements']:
    if element['type'] == 'way' and 'nodes' in element:
        coords = []
        for node_id in element['nodes']:
            if node_id in nodes:
                coords.append(nodes[node_id])  # Asociar la coordenada de cada nodo al taxiway
        if coords:  # Solo añadir el taxiway si tiene nodos asociados
            runways.append(coords)

# Verificación de los runways agregados
if runways:
    print(f"Total de runways encontrados: {len(runways)}")
else:
    print("No se encontraron runways.")

# Crear un mapa interactivo de OpenStreetMap centrado en Arlanda
center_lat = np.mean([coord[0] for taxiway in runways for coord in taxiway])
center_lon = np.mean([coord[1] for taxiway in runways for coord in taxiway])

m = folium.Map(location=[center_lat, center_lon], zoom_start=13)
folium.TileLayer('CartoDB Positron').add_to(m)

for idx, runway in enumerate(runways, start=1):
    folium.PolyLine(locations=runway, color='#333333', weight=2.5, opacity=1).add_to(m)
    # Afegir marcador al centre del runway
    lat_center = np.mean([pt[0] for pt in runway])
    lon_center = np.mean([pt[1] for pt in runway])
    folium.map.Marker(
        [lat_center, lon_center],
        icon=folium.DivIcon(html=f'<div style="font-size:12px; color:#333;"><b>RWY {idx}</b></div>')
    ).add_to(m)
    

# Definir la consulta Overpass API para obtener los taxiways de Arlanda (nodos y ways)
overpass_url = "http://overpass-api.de/api/interpreter"
overpass_query = """
[out:json];
area[name="Stockholm-Arlanda flygplats"]->.a;
(
  way(area.a)["aeroway"="taxiway"];
  node(w);
);
out body;
"""

# Hacer la solicitud a la API de Overpass
response = requests.get(overpass_url, params={'data': overpass_query})

# Procesar los datos obtenidos de la API de Overpass
data = response.json()

# Extraer los nodos
nodes = {}
for element in data['elements']:
    if element['type'] == 'node':
        nodes[element['id']] = (element['lat'], element['lon'])

# Extraer los taxiways (ways) y asociarlos con los nodos
taxiways = []
for element in data['elements']:
    if element['type'] == 'way' and 'nodes' in element:
        coords = []
        for node_id in element['nodes']:
            if node_id in nodes:
                coords.append(nodes[node_id])  # Asociar la coordenada de cada nodo al taxiway
        if coords:  # Solo añadir el taxiway si tiene nodos asociados
            taxiways.append(coords)

# Verificación de los taxiways agregados
if taxiways:
    print(f"Total de taxiways encontrados: {len(taxiways)}")
else:
    print("No se encontraron taxiways.")

# Agregar los taxiways al mapa (sin invertir las coordenadas)
for taxiway in taxiways:
    # Opción 1: Usar directamente taxiway
    folium.PolyLine(locations=taxiway, color='#4b6eaf', weight=2.5, opacity=1).add_to(m)
    
# Definir la consulta Overpass API para obtener los aprons de Arlanda (nodos y ways)
overpass_url = "http://overpass-api.de/api/interpreter"
overpass_query = """
[out:json];
area[name="Stockholm-Arlanda flygplats"]->.a;
(
  way(area.a)["aeroway"="apron"];
  node(w);
);
out body;
"""

# Hacer la solicitud a la API de Overpass
response = requests.get(overpass_url, params={'data': overpass_query})

# Procesar los datos obtenidos de la API de Overpass
data = response.json()

# Extraer los nodos
nodes = {}
for element in data['elements']:
    if element['type'] == 'node':
        nodes[element['id']] = (element['lat'], element['lon'])

# Extraer los aprons (ways) y asociarlos con los nodos
aprons = []
for element in data['elements']:
    if element['type'] == 'way' and 'nodes' in element:
        coords = []
        for node_id in element['nodes']:
            if node_id in nodes:
                coords.append(nodes[node_id])  # Asociar la coordenada de cada nodo al taxiway
        if coords:  # Solo añadir el taxiway si tiene nodos asociados
            aprons.append(coords)

# Verificación de los aprons agregados
if aprons:
    print(f"Total de aprons encontrados: {len(aprons)}")
else:
    print("No se encontraron aprons.")

for idx, apron in enumerate(aprons, start=1):
    folium.PolyLine(locations=apron, color='#bbbbbb', weight=2.5, opacity=1).add_to(m)
    # Afegir marcador al centre del apron
    lat_center = np.mean([pt[0] for pt in apron])
    lon_center = np.mean([pt[1] for pt in apron])
    folium.map.Marker(
        [lat_center, lon_center],
        icon=folium.DivIcon(html=f'<div style="font-size:12px; color:#444;"><b>AP {idx}</b></div>')
    ).add_to(m)
    

# HTML para la leyenda
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

# Agregar la leyenda al mapa
m.get_root().html.add_child(folium.Element(legend_html))
m.save('arlanda_airport_map.html')
print("Map successfully saved as 'arlanda_airport_map.html'")
webbrowser.open('arlanda_airport_map.html')