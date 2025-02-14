import requests
import folium
from shapely.geometry import LineString
import numpy as np

# Definir la consulta Overpass API para obtener los parkings de Arlanda (nodos y ways)
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

# Hacer la solicitud a la API de Overpass
response = requests.get(overpass_url, params={'data': overpass_query})

# Procesar los datos obtenidos de la API de Overpass
data = response.json()

# Extraer los nodos
nodes = {}
for element in data['elements']:
    if element['type'] == 'node':
        nodes[element['id']] = (element['lat'], element['lon'])

# Extraer los parkings (ways) y asociarlos con los nodos
parkings = []
for element in data['elements']:
    if element['type'] == 'way' and 'nodes' in element:
        coords = []
        for node_id in element['nodes']:
            if node_id in nodes:
                coords.append(nodes[node_id])  # Asociar la coordenada de cada nodo al taxiway
        if coords:  # Solo añadir el taxiway si tiene nodos asociados
            parkings.append(coords)

# Verificación de los parkings agregados
if parkings:
    print(f"Total de parkings encontrados: {len(parkings)}")
else:
    print("No se encontraron parkings.")

# Crear un mapa interactivo de OpenStreetMap centrado en Arlanda
center_lat = np.mean([coord[0] for taxiway in parkings for coord in taxiway])
center_lon = np.mean([coord[1] for taxiway in parkings for coord in taxiway])

m = folium.Map(location=[center_lat, center_lon], zoom_start=13)
folium.TileLayer('Esri.WorldImagery').add_to(m)

# Agregar los parkings al mapa (sin invertir las coordenadas)
for taxiway in parkings:
    # Opción 1: Usar directamente taxiway
    folium.PolyLine(locations=taxiway, color='black', weight=2.5, opacity=1).add_to(m)
    

# HTML para la leyenda
legend_html = '''
    <div style="position: fixed; 
                top: 200px; left: 200px; width: 100px; height: 60px; 
                background-color: white; z-index:9999; font-size:14px; 
                padding: 5px; border-radius:5px; box-shadow:2px 2px 6px rgba(0,0,0,0.5);">
        <span style="background-color: black; border-radius: 50%; width: 15px; height: 15px; display: inline-block; margin-right: 5px;"></span> Parking positions <br>
    </div>
'''
m.get_root().html.add_child(folium.Element(legend_html))
m.save('arlanda_parkings_map.html')
print("Map successfully saved as 'arlanda_parkings_map.html'")