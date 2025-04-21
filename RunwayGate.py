import pandas as pd
import glob
import os
from shapely.geometry import Point
from classify_flight import classify_flight

def add_runways_to_occupancy(df_occupancy, trajectory_df, runway_lines, df_apron_nodes):
    df = df_occupancy.copy()

    def find_runway_for_callsign(callsign):
        flight = trajectory_df[trajectory_df['callsign_group'] == callsign]
        flight = flight[flight['onground'] == True].sort_values('timestamp')

        if len(flight) == 0:
            return None
        
        flight_type = classify_flight(flight, callsign, df_apron_nodes)

        if flight_type == 'Arrival':
            point = Point(flight.iloc[0]['longitude'], flight.iloc[0]['latitude'])  # Primer punt després d’aterrar
        elif flight_type == 'Departure':
            point = Point(flight.iloc[-1]['longitude'], flight.iloc[-1]['latitude'])  # Últim punt abans de marxar
        else:
            return None

        min_dist = float('inf')
        used_runway = None

        for rwy_id, line in enumerate(runway_lines):
            dist = point.distance(line) * 111139  # graus → metres
            if dist < min_dist:
                min_dist = dist
                used_runway = rwy_id + 1

        return used_runway

    df['arrival_runway'] = df['arrival_callsign'].apply(find_runway_for_callsign)
    df['departure_runway'] = df['departure_callsign'].apply(find_runway_for_callsign)
    
    return df


def runway_percentages(df, column, runways):
    total = df[column].notna().sum()
    counts = df[column].value_counts()
    return {rwy: round(100 * counts.get(rwy, 0) / total, 1) for rwy in runways}



import pandas as pd
import os
import glob

# Llegim tots els CSVs
folder = r"C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\October\GateOccupancy"
csv_files = glob.glob(os.path.join(folder, "GateOccupancy*.csv"))

df_list = [pd.read_csv(f) for f in csv_files]
df_all = pd.concat(df_list, ignore_index=True)

# print("Total d'operacions analitzades:", len(df_all))

# Conversions
df_all['arrival_runway'] = df_all['arrival_runway'].astype(str)
df_all['departure_runway'] = df_all['departure_runway'].astype(str)
df_all['gate'] = df_all['gate'].astype(str)

# Mapping real
arrival_map = {'1': '19R', '2': '19L', '3': '26'}
departure_map = {'1': '01L', '2': '01R', '3': '26'}

df_all['arrival_runway'] = df_all['arrival_runway'].map(arrival_map)
df_all['departure_runway'] = df_all['departure_runway'].map(departure_map)

# Seleccionem les 20 gates amb més operacions
op_counts = df_all['gate'].value_counts().head(20).index.tolist()
df_top = df_all[df_all['gate'].isin(op_counts)]

# Càlcul
results = []

for gate in sorted(op_counts, key=lambda g: df_top[df_top['gate'] == g].shape[0], reverse=True):
    df_gate = df_top[df_top['gate'] == gate]

    arr_counts = df_gate['arrival_runway'].value_counts()
    dep_counts = df_gate['departure_runway'].value_counts()
    total_movements = arr_counts.sum() + dep_counts.sum()

    row = {
        'Gate': gate,
        'Arrival 19R (%)': round(100 * arr_counts.get('19R', 0) / arr_counts.sum(), 1),
        'Arrival 19L (%)': round(100 * arr_counts.get('19L', 0) / arr_counts.sum(), 1),
        'Arrival 26 (%)': round(100 * arr_counts.get('26', 0) / arr_counts.sum(), 1),
        'Departure 01L (%)': round(100 * dep_counts.get('01L', 0) / dep_counts.sum(), 1),
        'Departure 01R (%)': round(100 * dep_counts.get('01R', 0) / dep_counts.sum(), 1),
        'Departure 26 (%)': round(100 * dep_counts.get('26', 0) / dep_counts.sum(), 1),
        'Total Ops': df_gate.shape[0]
    }

    results.append(row)

# Export
df_result = pd.DataFrame(results)
df_result.to_csv(os.path.join(folder, "RunwayGateUsage.csv"), index=False)
