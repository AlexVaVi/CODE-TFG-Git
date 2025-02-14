# conversion.py
import numpy as np

def latlon_to_xy(lat, lon, ref_lat, ref_lon):
    """
    Converts arrays of latitudes and longitudes (in degrees) to x, y coordinates (in meters) 
    using an equirectangular projection with the reference point (ref_lat, ref_lon).
    """
    R = 6371000.0  # Radio de la Tierra en metros
    lat_rad = np.radians(lat)
    lon_rad = np.radians(lon)
    ref_lat_rad = np.radians(ref_lat)
    ref_lon_rad = np.radians(ref_lon)
    x = R * (lon_rad - ref_lon_rad) * np.cos(ref_lat_rad)
    y = R * (lat_rad - ref_lat_rad)
    return x, y

def xy_to_latlon(x, y, ref_lat, ref_lon):
    """
    Converts x, y coordinates (in meters) to latitude and longitude (in degrees) 
    using the inverse projection with the same reference point.    
    """
    R = 6371000.0
    ref_lat_rad = np.radians(ref_lat)
    lat_rad = y / R + ref_lat_rad
    lon_rad = x / (R * np.cos(ref_lat_rad)) + np.radians(ref_lon)
    lat = np.degrees(lat_rad)
    lon = np.degrees(lon_rad)
    return lat, lon
