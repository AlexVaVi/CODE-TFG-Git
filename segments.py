import numpy as np
import folium
import webbrowser
from shapely.geometry import Point, LineString
from conversion import xy_to_latlon

def plot_segments(closest_segments, ref_lat, ref_lon):
    """
    Plots each taxiway segment (LineString) from closest_segments on a Folium map,
    converting metric coordinates to lat/lon. Each segment is drawn as a green polyline,
    and its midpoint is labeled with its index number.
    
    Parameters:
      closest_segments: list of LineString objects.
      ref_lat, ref_lon: reference coordinates for conversion (e.g., airport center).
    
    Returns:
      A Folium map with numbered segments.
    """
    
    # Limit to the first num_segments unique segments
    segments_to_plot = closest_segments[:20]
    
    
    # Create a Folium map centered on the reference point
    m = folium.Map(location=[ref_lat, ref_lon], zoom_start=16)
    
    # Iterate over each segment with an index
    for idx, seg in enumerate(segments_to_plot):
        # Skip if segment is None
        if seg is None:
            continue
        
        # Extract x and y coordinates from the segment (assumed to be in meters)
        xs, ys = seg.xy
        xs = np.array(xs)
        ys = np.array(ys)
        
        # Convert metric coordinates to lat/lon
        lat_vals, lon_vals = xy_to_latlon(xs, ys, ref_lat, ref_lon)
        coords = list(zip(lat_vals, lon_vals))
        
        # Draw the segment as a green polyline
        folium.PolyLine(locations=coords, color='green', weight=3, opacity=0.8,
                        tooltip=f"Segment {idx}").add_to(m)
        
        # Determine the midpoint of the segment for labeling
        mid_idx = len(coords) // 2
        mid_point = coords[mid_idx]
        
        # Place a marker with the segment index at the midpoint
        folium.Marker(
            location=mid_point,
            icon=folium.DivIcon(
                html=f"""<div style="font-size: 14pt; color: blue;">{idx}</div>"""
            ),
            tooltip=f"Segment {idx}"
        ).add_to(m)
    
    # Save and open the map in the default web browser
    m.save("segments_with_numbers.html")
    webbrowser.open("segments_with_numbers.html")
    return m
