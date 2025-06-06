import numpy as np
import folium
import webbrowser
from shapely.geometry import Point, LineString
from conversion import xy_to_latlon

def plot_segments(closest_segments, ref_lat, ref_lon):
    """
    Plots up to 20 taxiway segments (LineString) on a Folium map,
    converting from local metric coordinates to geographic lat/lon.
    Each segment is drawn in green and labeled with its index.

    Parameters:
      closest_segments: list of LineString objects (in XY coordinates).
      ref_lat, ref_lon: reference latitude and longitude for conversion.

    Returns:
      A Folium map displaying the segments with numeric labels.
      Automatically opens the result in the default web browser.
    """

    # Limit the number of segments to visualize
    segments_to_plot = closest_segments[:20]

    # Create a Folium map centered on the reference point
    m = folium.Map(location=[ref_lat, ref_lon], zoom_start=16)

    # Plot each segment with its index
    for idx, seg in enumerate(segments_to_plot):
        if seg is None:
            continue

        # Extract XY coordinates and convert them to lat/lon
        xs, ys = seg.xy
        lat_vals, lon_vals = xy_to_latlon(np.array(xs), np.array(ys), ref_lat, ref_lon)
        coords = list(zip(lat_vals, lon_vals))

        # Draw the segment as a polyline
        folium.PolyLine(
            locations=coords,
            color='green',
            weight=3,
            opacity=0.8,
            tooltip=f"Segment {idx}"
        ).add_to(m)

        # Place a numeric marker at the midpoint
        mid_idx = len(coords) // 2
        mid_point = coords[mid_idx]

        folium.Marker(
            location=mid_point,
            icon=folium.DivIcon(
                html=f"""<div style="font-size: 14pt; color: blue;">{idx}</div>"""
            ),
            tooltip=f"Segment {idx}"
        ).add_to(m)

    # Save the map to HTML and open it
    m.save("segments_with_numbers.html")
    webbrowser.open("segments_with_numbers.html")
    return m
