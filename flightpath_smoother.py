import numpy as np
import networkx as nx
import folium
import webbrowser
from shapely.geometry import Point, LineString
from shapely.ops import linemerge
from conversion import latlon_to_xy, xy_to_latlon

def sub_line_geometry(seg, p_start, p_end, n=20):
    if p_start > p_end:
        p_start, p_end = p_end, p_start
    ps = np.linspace(p_start, p_end, n)
    coords = [seg.interpolate(p) for p in ps]
    return LineString([(pt.x, pt.y) for pt in coords])

def flight_path_smoother(corrected_lat, corrected_lon, unique_segments, ref_lat, ref_lon):

    x_m, y_m = latlon_to_xy(corrected_lat, corrected_lon, ref_lat, ref_lon)
    filtered_pts = [Point(x_m[i], y_m[i]) for i in range(len(x_m))]

    G = nx.Graph()
    
    # Agrega cada punto filtrado como nodo
    for pt in filtered_pts:
        node = (pt.x, pt.y)
        if node not in G:
            G.add_node(node, geometry=pt)

    # Agrega los extremos de cada segmento
    for seg in unique_segments:
        start = Point(seg.coords[0])
        end   = Point(seg.coords[-1])
        for p in [start, end]:
            node = (p.x, p.y)
            if node not in G:
                G.add_node(node, geometry=p)

    # Intersecciones
    for i in range(len(unique_segments)):
        for j in range(i+1, len(unique_segments)):
            seg1 = unique_segments[i]
            seg2 = unique_segments[j]
            inter = seg1.intersection(seg2)
            if not inter.is_empty:
                if inter.geom_type == 'Point':
                    node = (inter.x, inter.y)
                    if node not in G:
                        G.add_node(node, geometry=inter)
                elif inter.geom_type == 'MultiPoint':
                    for p in inter.geoms:
                        node = (p.x, p.y)
                        if node not in G:
                            G.add_node(node, geometry=p)

    # Construye aristas con geometría curva
    tol = 1e-6
    for seg in unique_segments:
        nodes_on_seg = []
        for node, data in G.nodes(data=True):
            pt = data['geometry']
            p  = seg.project(pt)
            proj_pt = seg.interpolate(p)
            if pt.distance(proj_pt) < tol:
                nodes_on_seg.append((node, p))
        # Ordena los nodos por parámetro
        nodes_on_seg.sort(key=lambda tup: tup[1])
        
        # Crea aristas consecutivas con la geometría real del sub-tramo
        for k in range(len(nodes_on_seg)-1):
            node1, p1 = nodes_on_seg[k]
            node2, p2 = nodes_on_seg[k+1]
            # Geometría real del sub-tramo [p1, p2]
            line_geom = sub_line_geometry(seg, p1, p2, n=20)
            edge_length = line_geom.length
            G.add_edge(node1, node2, weight=edge_length, geometry=line_geom)

    # Función para encontrar el nodo más cercano
    def find_nearest_node(pt, graph):
        min_dist = float('inf')
        nearest = None
        for node, data in graph.nodes(data=True):
            d = pt.distance(data['geometry'])
            if d < min_dist:
                min_dist = d
                nearest = node
        return nearest

    start_node = find_nearest_node(filtered_pts[0], G)
    end_node   = find_nearest_node(filtered_pts[-1], G)

    try:
        path_nodes = nx.shortest_path(G, source=start_node, target=end_node, weight='weight')
    except Exception as e:
        print("Error computing shortest path:", e)
        return []

    path_lines = []
    for i in range(len(path_nodes)-1):
        u = path_nodes[i]
        v = path_nodes[i+1]
        edge_data = G.get_edge_data(u, v)
        if edge_data and 'geometry' in edge_data:
            path_lines.append(edge_data['geometry'])

    if path_lines:
        merged_path = linemerge(path_lines)
    else:
        merged_path = None

    if merged_path is None:
        merged_path_coords = []
    else:
        xs, ys = np.array(merged_path.xy[0]), np.array(merged_path.xy[1])
        final_lat, final_lon = xy_to_latlon(xs, ys, ref_lat, ref_lon)
        merged_path_coords = list(zip(final_lat, final_lon))

    center_lat = np.mean(final_lat) if merged_path_coords else ref_lat
    center_lon = np.mean(final_lon) if merged_path_coords else ref_lon
    m = folium.Map(location=[center_lat, center_lon], zoom_start=16)
    folium.TileLayer('CartoDB Positron').add_to(m)

    
    if merged_path_coords:
        folium.PolyLine(locations=merged_path_coords, color='#4b6eaf', weight=4, opacity=0.8,
                        tooltip="Forced Taxiway Path").add_to(m)

    for i in range(len(corrected_lat)):
        folium.CircleMarker(
        location=[corrected_lat[i], corrected_lon[i]],
        radius=1,           # Tamaño del círculo
        color='#333333',      # Contorno negro
        fill=True,
        fill_color='#333333', # Relleno negro
        fill_opacity=1.0,
        # tooltip=f"Filtered point {i}"  # Puedes descomentar si quieres mostrar el índice al pasar el ratón
    ).add_to(m)

    
    m.save("flight_path_smoother.html")
    webbrowser.open("flight_path_smoother.html")
