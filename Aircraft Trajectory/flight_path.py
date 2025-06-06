import folium
import pandas as pd
import numpy as np
import classify_flight as cf
import webbrowser

def flight_path(flight_df, callsign_nr, df_apron_nodes):
    # Filter the flight data for the given callsign number
    df_flight = flight_df[(flight_df['callsign_group'] == callsign_nr)]
    callsign = df_flight['callsign'].unique()[0]
    num_points = len(df_flight)

    # Compute total ground time from the first to the last recorded timestamp
    first_time = pd.to_datetime(df_flight['timestamp'].iloc[0])
    last_time = pd.to_datetime(df_flight['timestamp'].iloc[-1])
    elapsed_time = last_time - first_time
    elapsed_time_seconds = elapsed_time.total_seconds()
    hours = int(elapsed_time_seconds // 3600)
    minutes = int((elapsed_time_seconds % 3600) // 60)
    seconds = int((elapsed_time_seconds % 3600) % 60)
    formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    # Classify the flight as arrival or departure
    type = cf.classify_flight(flight_df, callsign_nr, df_apron_nodes)

    # Calculate the center of the trajectory for map centering
    center_lat = df_flight['latitude'].mean()
    center_lon = df_flight['longitude'].mean()

    # Create and configure the folium map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=16)
    folium.TileLayer('CartoDB Positron').add_to(m)

    # Draw the trajectory using polylines (in blue)
    for i in range(1, len(df_flight)):
        folium.PolyLine(
            locations=[(df_flight.iloc[i-1]['latitude'], df_flight.iloc[i-1]['longitude']),
                       (df_flight.iloc[i]['latitude'], df_flight.iloc[i]['longitude'])],
            color='#4b6eaf',
            weight=4,
            opacity=0.8
        ).add_to(m)

    # Save the map as an interactive HTML file
    m.save("flight_path.html")

    # Print basic information for traceability
    print(f"Number of points for flight {callsign}: {num_points}")
    print(f"Ground time spent for {callsign}: {elapsed_time}")
    print(f"Map successfully saved as 'flight_path.html'")

    # Automatically open the map in the default web browser
    webbrowser.open("flight_path.html")

    return m