import pandas as pd
from shapely.geometry import Point
from classify_flight import classify_flight
from ParkingDetection import find_parking
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def compute_gate_blocked_intervals(trajectory_df, parking_lines, df_apron_nodes):
    arrivals = []
    departures = []
    
    total_flights = 0
    unknown_flights = 0
    no_gate_flights = 0

    for callsign in trajectory_df['callsign_group'].unique():
        total_flights += 1
        traj = trajectory_df[trajectory_df['callsign_group'] == callsign].sort_values('timestamp')
        flight_type, gate_id, distance = find_parking(traj, callsign, parking_lines, df_apron_nodes)

        if flight_type == "Unknown":
            unknown_flights += 1
            continue

        if gate_id is None:
            no_gate_flights += 1
            continue

        if flight_type == "Arrival":
            last_point_time = pd.to_datetime(traj.iloc[-1]['timestamp'])
            arrivals.append({'gate': gate_id, 'timestamp': last_point_time, 'callsign_group': callsign})

        elif flight_type == "Departure":
            first_point_time = pd.to_datetime(traj.iloc[0]['timestamp'])
            departures.append({'gate': gate_id, 'timestamp': first_point_time, 'callsign_group': callsign})
            
    print("📊 Total flights in input:", total_flights)
    print("❌ Discarded (Unknown flight type):", unknown_flights)
    print("❌ Discarded (No gate assigned):", no_gate_flights)
    print("✅ Accepted arrivals:", len(arrivals))
    print("✅ Accepted departures:", len(departures))

    df_arrivals = pd.DataFrame(arrivals)
    df_departures = pd.DataFrame(departures)

    # Merge arrivals and next departures for each gate
    gate_blocked_intervals = []

    for gate_id in set(df_arrivals['gate']).intersection(set(df_departures['gate'])):
        arr_gate = df_arrivals[df_arrivals['gate'] == gate_id].sort_values('timestamp')
        dep_gate = df_departures[df_departures['gate'] == gate_id].sort_values('timestamp')

        dep_index = 0

        for _, arr in arr_gate.iterrows():
            # Buscar la primera departure posterior a la arrival
            while dep_index < len(dep_gate) and dep_gate.iloc[dep_index]['timestamp'] <= arr['timestamp']:
                dep_index += 1

            if dep_index < len(dep_gate):
                dep = dep_gate.iloc[dep_index]
                gate_blocked_intervals.append({
                    'gate': gate_id,
                    'start_time': arr['timestamp'],
                    'end_time': dep['timestamp'],
                    'duration_minutes': (dep['timestamp'] - arr['timestamp']).total_seconds() / 60,
                    'arrival_callsign': arr['callsign_group'],
                    'departure_callsign': dep['callsign_group']
                })
                dep_index += 1  # pasar al siguiente departure

    return pd.DataFrame(gate_blocked_intervals)




def plot_gate_occupancy_chart(df_blocked, top_n=10):
    df = df_blocked.copy()
    df['duration'] = df['end_time'] - df['start_time']
    df['gate'] = df['gate'].astype(str)  
    # df = df[df['duration'] < pd.Timedelta(hours=12)]

    duration_total = df.groupby('gate')['duration'].sum()
    top_gates = duration_total.sort_values(ascending=False).head(top_n)
    print("🔍 Duración total por gate (orden real):")
    print(top_gates)

    gate_order = top_gates.index.tolist()
    df = df[df['gate'].isin(gate_order)]

    fig, ax = plt.subplots(figsize=(14, 6))
    color = '#444444'

    for gate in gate_order:
        df_gate = df[df['gate'] == gate]
        for _, row in df_gate.iterrows():
            ax.barh(
                y=gate,
                width=row['duration'],
                left=row['start_time'],
                height=0.4,
                color=color,
                edgecolor='black'
            )

    ax.set_yticks(gate_order)
    ax.set_yticklabels([f"Gate {g}" for g in gate_order], fontsize=12)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)
    ax.invert_yaxis()
    plt.tight_layout()
    plt.show()






def plot_gate_occupancy_by_operations(df_blocked, top_n=10):
    df = df_blocked.copy()
    df['duration'] = df['end_time'] - df['start_time']

    # custom_colors = [
    #     '#7fbfff', '#3e5c76', '#bdbdbd', '#2c3e50',
    #     '#5388b3', '#444444', '#4C78A8',
    #     '#8ca0b3', '#6e7f91', '#a3b8cc'  # tonos de refuerzo si hay más de 7
    # ]

    # Obtener los top_n gates con más ocupaciones (más filas)
    top_gates = (
        df['gate'].value_counts()
        .head(top_n)
        .index
    )
    df = df[df['gate'].isin(top_gates)]

    # Ordenar los gates para el eje Y
    gate_order = df['gate'].value_counts().loc[top_gates].index.tolist()


    # Crear gráfico
    fig, ax = plt.subplots(figsize=(14, 6))
    colors = plt.cm.tab20.colors

    for i, gate in enumerate(gate_order):
        df_gate = df[df['gate'] == gate]
        color = '#4C78A8'
        for _, row in df_gate.iterrows():
            ax.barh(
                y=i,
                width=row['duration'],
                left=row['start_time'],
                height=0.4,
                color=color,
                edgecolor='black'
            )

    ax.set_yticks(range(len(gate_order)))
    ax.set_yticklabels([f"Gate {g}" for g in gate_order], fontsize=12)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)
    # ax.grid(True)
    ax.invert_yaxis()

    plt.tight_layout()
    plt.show()


def remove_overlaps_by_gate(df_occupancy):
    df_clean = []

    for gate_id in df_occupancy['gate'].unique():
        df_gate = df_occupancy[df_occupancy['gate'] == gate_id].sort_values('start_time').reset_index(drop=True)

        last_end_time = pd.Timestamp.min

        for _, row in df_gate.iterrows():
            if row['start_time'] >= last_end_time:
                df_clean.append(row)
                last_end_time = row['end_time']
            else:
                # Solapament detectat → es descarta
                continue

    return pd.DataFrame(df_clean)






import os
import glob

def compute_hourly_gate_occupancy_avg_from_folder(folder_path):

    csv_files = glob.glob(os.path.join(folder_path, "GateOccupancy*.csv"))

    df_list = [pd.read_csv(f, parse_dates=['start_time', 'end_time']) for f in csv_files]
    df = pd.concat(df_list, ignore_index=True)

    all_hours = pd.date_range(
        start=df['start_time'].min().floor('D'),
        end=df['end_time'].max().ceil('D'),
        freq='1h'
    )

    occupancy_by_hour = []

    for h in all_hours:
        count = ((df['start_time'] <= h) & (df['end_time'] > h)).sum()
        occupancy_by_hour.append({'hour': h.time(), 'weekday': h.weekday(), 'count': count})

    df_occ = pd.DataFrame(occupancy_by_hour)

    avg_by_hour = (
        df_occ.groupby('hour')
        .agg(avg_occupied_gates=('count', 'mean'))
        .reset_index()
    )

    return avg_by_hour


def plot_avg_gate_occupancy(avg_hourly, max_capacity=30, from_hour=1, to_hour=22):
    """
    Plots the average number of gates occupied per hour, optionally filtering the hour range.

    Parameters:
    - avg_hourly: DataFrame with 'hour' (as datetime.time or int) and 'avg_occupied_gates'
    - from_hour: first hour to include (default: 1)
    - to_hour: last hour to include (default: 23)
    """
    import matplotlib.pyplot as plt

    # Convertim a enters les hores
    avg_hourly['hour_int'] = avg_hourly['hour'].apply(lambda t: t.hour if hasattr(t, 'hour') else int(t))

    # Filtrar rang d'hores
    df_filtered = avg_hourly[(avg_hourly['hour_int'] >= from_hour) & (avg_hourly['hour_int'] <= to_hour)]

    hour_labels = [h.strftime('%H:%M') for h in df_filtered['hour']]

    x = list(range(len(df_filtered)))  # posicions x numèriques

    y = df_filtered['avg_occupied_gates']
    
    # Gràfica
    plt.figure(figsize=(14, 6))
    plt.plot(x, y, marker='o', color='#4C78A8', label='Average occupied gates')

    plt.fill_between(x, y, color='#4C78A8', alpha=0.5)
    
    if max_capacity:
        plt.axhline(y=max_capacity, color='#444444', linestyle='--', label='Max gate capacity')

    plt.legend()
    
    ax = plt.gca()
    ax.set_axisbelow(True)
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.xticks(ticks=x, labels=hour_labels, rotation=45)
    plt.grid(True)
    plt.ylabel('Average Gates Occupied', fontsize=12)
    plt.tick_params(labelsize=12)
    plt.tight_layout()
    plt.show()
    
#UNIQUE GATES   
def get_unique_gates_from_folder(folder_path, threshold=15):
    csv_files = glob.glob(os.path.join(folder_path, "GateOccupancy*.csv"))
    df_all = pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True)

    df_all['gate'] = df_all['gate'].astype(str)
    gate_counts = df_all['gate'].value_counts()

    active_gates = gate_counts[gate_counts > threshold].index.tolist()

    return active_gates, len(active_gates)
