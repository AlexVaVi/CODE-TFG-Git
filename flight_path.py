import folium
import pandas as pd
import numpy as np
import classify_flight as cf
import webbrowser 

def flight_path(flight_df, callsign_nr, runway_nodes_df):

    df_flight = flight_df[(flight_df['callsign_group'] == callsign_nr)]
    callsign = df_flight['callsign'].unique()[0]  
    num_points = len(df_flight)

    first_time = pd.to_datetime(df_flight['timestamp'].iloc[0])
    last_time = pd.to_datetime(df_flight['timestamp'].iloc[-1])
    elapsed_time = last_time - first_time
    elapsed_time_seconds = elapsed_time.total_seconds()
    hours = int(elapsed_time_seconds // 3600)
    minutes = int((elapsed_time_seconds % 3600) // 60)
    seconds = int((elapsed_time_seconds % 3600) % 60)
    formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    #type flight
    type = cf.classify_flight(flight_df, callsign_nr, runway_nodes_df)
    
    # Centra el mapa en el punto medio de la trayectoria
    center_lat = df_flight['latitude'].mean()
    center_lon = df_flight['longitude'].mean()

    # Crea un mapa centrado en la ubicación del vuelo
    m = folium.Map(location=[center_lat, center_lon], zoom_start=16)
    folium.TileLayer('CartoDB Positron').add_to(m)

    # Dibuja las líneas de la trayectoria en azul
    for i in range(1, len(df_flight)):
        folium.PolyLine(
            locations=[(df_flight.iloc[i-1]['latitude'], df_flight.iloc[i-1]['longitude']),
                    (df_flight.iloc[i]['latitude'], df_flight.iloc[i]['longitude'])],
            color='#4b6eaf',  # Traza toda la ruta en azul
            weight=4,
            opacity=0.8
        ).add_to(m)
        
    for i in range(len(df_flight)):
        folium.CircleMarker(
        location=[df_flight.iloc[i]['latitude'], df_flight.iloc[i]['longitude']],
        radius=1,           # Tamaño del círculo
        color='#333333',      # Contorno negro
        fill=True,
        fill_color='#333333', # Relleno negro
        fill_opacity=1.0,
        # tooltip=f"Filtered point {i}"  # Puedes descomentar si quieres mostrar el índice al pasar el ratón
    ).add_to(m)

    # Añadir un texto al mapa con el tiempo de tierra
    html = f"""
    <div style="position: fixed;
                top: 10px; right: 20px; width: 250px; height: 50px;
                background-color: white; z-index:9999; font-size:14px;
                padding: 5px; border-radius:5px; box-shadow:2px 2px 6px rgba(0,0,0,0.5);">
        Ground time for {callsign}: {formatted_time}
        {type}
    </div>
    """
    m.get_root().html.add_child(folium.Element(html))

    # Guarda el mapa en un archivo HTML
    m.save("flight_path.html")  

    print(f"Number of points for flight {callsign}: {num_points}")
    print(f"Ground time spent for {callsign}: {elapsed_time}")
    print(f"Map successfully saved as 'flight_path.html'")
    
    webbrowser.open("flight_path.html")
    
    return m

