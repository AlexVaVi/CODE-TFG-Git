from geopy.distance import geodesic

def trim_parking(df, distance_threshold=5, min_stopped_duration=120):
    """
    Trim the trajectory after the aircraft remains within a small area
    for a prolonged period, indicating that it has likely stopped (parking phase).

    Parameters:
    ----------
    df : pandas.DataFrame
        The trajectory data for a single flight (callsign_group).
    distance_threshold : float, default=5
        Maximum radius in meters considered as a "static" zone.
    min_stopped_duration : float, default=120
        Minimum duration (in seconds) the aircraft must remain static before trimming.
        
    Returns:
    -------
    pandas.DataFrame
        Trimmed trajectory where the static phase has been removed.
    """
    df = df.sort_values(by='timestamp').reset_index(drop=True)
    
    reference_point = (df.loc[0, 'latitude'], df.loc[0, 'longitude'])
    static_time = 0
    trim_index = None

    for i in range(1, len(df)):
        current_point = (df.loc[i, 'latitude'], df.loc[i, 'longitude'])
        distance = geodesic(reference_point, current_point).meters
        time_diff = (df.loc[i, 'timestamp'] - df.loc[i - 1, 'timestamp']).total_seconds()

        if distance <= distance_threshold:
            static_time += time_diff
            if static_time >= min_stopped_duration:
                trim_index = i
                break
        else:
            reference_point = current_point
            static_time = 0

    if trim_index:
        df = df.iloc[:trim_index]

    return df
