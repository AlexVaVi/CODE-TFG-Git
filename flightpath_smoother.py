import numpy as np
import networkx as nx
import folium
import webbrowser
from shapely.geometry import Point, LineString
from shapely.ops import linemerge
from conversion import latlon_to_xy, xy_to_latlon
from ApronAnalysis import find_apron
import pandas as pd
from geopy.distance import geodesic

def flight_path_smoother(corrected_lat, corrected_lon, unique_segments, ref_lat, ref_lon):

    df_apron = pd.read_csv(r'C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\arlanda_airport_nodes.csv')
    df_apron = df_apron[df_apron['type'] == 'apron']

    # Funció interna: separa segments entre aprons i infra
    def split_apron_segments(latitudes, longitudes):
        segments = []
        current_segment = {"lat": [], "lon": []}
        inside_apron = False
        for i in range(len(latitudes)):
            lat, lon = latitudes[i], longitudes[i]
            in_apron = find_apron(lat, lon, df_apron) is not None
            if in_apron:
                if not inside_apron and current_segment["lat"]:
                    segments.append({"type": "infra", "lat": current_segment["lat"], "lon": current_segment["lon"]})
                    current_segment = {"lat": [], "lon": []}
                inside_apron = True
                current_segment["lat"].append(lat)
                current_segment["lon"].append(lon)
            else:
                if inside_apron:
                    current_segment["lat"].append(lat)
                    current_segment["lon"].append(lon)
                    segments.append({"type": "apron", "lat": current_segment["lat"], "lon": current_segment["lon"]})
                    current_segment = {"lat": [], "lon": []}
                    inside_apron = False
                else:
                    current_segment["lat"].append(lat)
                    current_segment["lon"].append(lon)
        if current_segment["lat"]:
            segment_type = "apron" if inside_apron else "infra"
            segments.append({"type": segment_type, "lat": current_segment["lat"], "lon": current_segment["lon"]})
        return segments

    m = folium.Map(location=[np.mean(corrected_lat), np.mean(corrected_lon)], zoom_start=16)
    folium.TileLayer('CartoDB Positron').add_to(m)

    segments = split_apron_segments(corrected_lat, corrected_lon)
    prev_end = None
    
    for seg in segments:
        if seg["type"] == "apron":
            folium.PolyLine(list(zip(seg["lat"], seg["lon"])), color="#4b6eaf", weight=4, opacity=0.8,
                            tooltip="Apron segment").add_to(m)
        else:
            # Infraestructura: fer servir NetworkX
            x_m, y_m = latlon_to_xy(seg["lat"], seg["lon"], ref_lat, ref_lon)
            filtered_pts = [Point(x_m[i], y_m[i]) for i in range(len(x_m))]

            G = nx.Graph()
            for pt in filtered_pts:
                G.add_node((pt.x, pt.y), geometry=pt)
            for segm in unique_segments:
                for p in [segm.coords[0], segm.coords[-1]]:
                    pt = Point(p)
                    G.add_node((pt.x, pt.y), geometry=pt)

            # Interseccions
            for i in range(len(unique_segments)):
                for j in range(i+1, len(unique_segments)):
                    inter = unique_segments[i].intersection(unique_segments[j])
                    if not inter.is_empty:
                        if inter.geom_type == 'Point':
                            G.add_node((inter.x, inter.y), geometry=inter)
                        elif inter.geom_type == 'MultiPoint':
                            for p in inter.geoms:
                                G.add_node((p.x, p.y), geometry=p)

            tol = 1e-6
            for segment in unique_segments:
                nodes_on_seg = []
                for node, data in G.nodes(data=True):
                    pt = data['geometry']
                    p = segment.project(pt)
                    proj_pt = segment.interpolate(p)
                    if pt.distance(proj_pt) < tol:
                        nodes_on_seg.append((node, p))
                nodes_on_seg.sort(key=lambda tup: tup[1])
                for k in range(len(nodes_on_seg)-1):
                    n1, p1 = nodes_on_seg[k]
                    n2, p2 = nodes_on_seg[k+1]
                    p1 = float(p1)
                    p2 = float(p2)
                    coords = [segment.interpolate(t) for t in np.linspace(p1, p2, 20)]
                    line_geom = LineString([(pt.x, pt.y) for pt in coords])
                    G.add_edge(n1, n2, weight=line_geom.length, geometry=line_geom)

            def nearest_node(pt):
                return min(G.nodes, key=lambda node: pt.distance(Point(node)))

            start_node = nearest_node(filtered_pts[0])
            end_node = nearest_node(filtered_pts[-1])

            try:
                path_nodes = nx.shortest_path(G, source=start_node, target=end_node, weight="weight")
                path_lines = []
                for i in range(len(path_nodes)-1):
                    u, v = path_nodes[i], path_nodes[i+1]
                    data = G.get_edge_data(u, v)
                    if data and "geometry" in data:
                        path_lines.append(data["geometry"])
                if path_lines:
                    merged = linemerge(path_lines)
                    xs, ys = merged.xy
                    xs = np.array(xs)
                    ys = np.array(ys)
                    lat_f, lon_f = xy_to_latlon(xs, ys, ref_lat, ref_lon)
                    folium.PolyLine(list(zip(lat_f, lon_f)), color="#4b6eaf", weight=4, opacity=0.8,
                                    tooltip="Infrastructure Path").add_to(m)
            except Exception as e:
                print(f"Path error: {e}")

        points = list(zip(seg["lat"], seg["lon"]))

        # --- Connectar visualment amb el tram anterior si cal ---
        if prev_end:
            first_pt = (seg["lat"][0], seg["lon"][0])
            dist = geodesic(prev_end, first_pt).meters
            if dist < 20:  # només si la separació és raonable
                folium.PolyLine([prev_end, first_pt], color="#4b6eaf", weight=4, opacity=0.8).add_to(m)

        # Actualitza l’últim punt
        prev_end = (seg["lat"][-1], seg["lon"][-1])
    
    # Afegeix punts corregits com a marcadors
    # for i in range(len(corrected_lat)):
    #     folium.CircleMarker(
    #         location=[corrected_lat[i], corrected_lon[i]],
    #         radius=1,
    #         color='#333333',
    #         fill=True,
    #         fill_color='#333333',
    #         fill_opacity=1.0
    #     ).add_to(m)
    
    # Timestamp sobre el primer punt
    folium.Marker(
        location=[corrected_lat[0], corrected_lon[0]],
        icon=folium.DivIcon(html=f"""
            <div style='font-size: 15px; color: black; font-weight: bold;'>
                🟢 {'04:10:38z'}
            </div>""")
    ).add_to(m)

    # Timestamp sobre l'últim punt
    folium.Marker(
        location=[corrected_lat[-1], corrected_lon[-1]],
        icon=folium.DivIcon(html=f"""
            <div style='font-size: 15px; color: black; font-weight: bold;'>
                🔴 {'04:23:13z'}
            </div>""")
    ).add_to(m)
        
    m.save("flight_path_smoother.html")
    webbrowser.open("flight_path_smoother.html")
