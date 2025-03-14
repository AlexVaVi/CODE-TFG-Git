import folium
import pandas as pd
import webbrowser
import classify_flight as cf  

def plot_flights_by_classification(flight_df, airport_nodes_df, callsign_limit, desired_classification="Arrival",
                                   zoom_start=16, output_html="flights_map.html"):
    
    # Create a map centered on the average coordinates of all flights
    center_lat = flight_df['latitude'].mean()
    center_lon = flight_df['longitude'].mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_start)
    classified_flights_count = 0
    
    # Iterate over each unique callsign in the flight DataFrame
    for callsign_group in sorted(flight_df['callsign_group'].unique()):
        if callsign_group > callsign_limit:
            break        
        
        # Filter the flight data for the current callsign and sort by timestamp
        df_flight = flight_df[flight_df['callsign_group'] == callsign_group]
        
        callsign_nr = df_flight['callsign_group'].iloc[0]
        callsign = df_flight['callsign'].iloc[0]
        
        classification = cf.classify_flight(df_flight, callsign_nr, airport_nodes_df)
        
        # Only plot the flight if its classification matches the desired one
        if classification != desired_classification:
            continue
        
        # Set color based on classification (green for Arrival, red for Departure)
        color = "green" if classification == "Arrival" else "red"
        
        # Create a list of (latitude, longitude) tuples representing the flight path
        points = list(zip(df_flight['latitude'], df_flight['longitude']))
        
        # Draw the flight path as a polyline on the map
        folium.PolyLine(locations=points, color=color, weight=3, opacity=0.8).add_to(m)
        
        # Markers for the start and end points
        folium.Marker(location=points[0],
                      popup=f"{callsign} - start",
                      icon=folium.Icon(color='blue', icon='play')).add_to(m)
        folium.Marker(location=points[-1],
                      popup=f"{callsign} - end",
                      icon=folium.Icon(color='black', icon='stop')).add_to(m)
        
        classified_flights_count += 1

    html = f"""
    <div style="position: fixed;
                top: 10px; left: 10px; width: 250px; height: 50px;
                background-color: white; z-index:9999; font-size:14px;
                padding: 5px; border-radius:5px; box-shadow:2px 2px 6px rgba(0,0,0,0.5);">
        Number of {desired_classification}s: {classified_flights_count}
    </div>
    """
    m.get_root().html.add_child(folium.Element(html))

    m.save(output_html)
    webbrowser.open(output_html)
    
    return m

