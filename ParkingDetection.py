from shapely.geometry import Point
from classify_flight import classify_flight

def find_parking(trajectory_df, callsign_nr, parking_lines, df_apron_nodes, threshold_parking=5):
    # Step 1: Classify the flight as Arrival or Departure
    flight_type = classify_flight(trajectory_df, callsign_nr, df_apron_nodes)

    if flight_type == "Unknown":
        return flight_type, None, None

    # Step 2: Select the relevant trajectory point (first or last)
    traj = trajectory_df[trajectory_df['callsign_group'] == callsign_nr]
    point = traj.iloc[-1] if flight_type == "Arrival" else traj.iloc[0]
    point_geom = Point(point['longitude'], point['latitude'])

    # Step 3: Find closest parking line
    min_distance = float('inf')
    closest_index = None

    for i, line in enumerate(parking_lines):
        distance = point_geom.distance(line) * 111139  # degrees to meters approx
        if distance < min_distance:
            min_distance = distance
            closest_index = i

    # Step 4: Apply parking threshold
    if min_distance > threshold_parking:
        return "Unknown", None, min_distance

    return flight_type, closest_index, min_distance
