import pandas as pd
from shapely.geometry import Point
from classify_flight import classify_flight
from ParkingDetection import find_parking
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import math
import numpy as np

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
                dep_index += 1 
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

    top_gates = (
        df['gate'].value_counts()
        .head(top_n)
        .index
    )
    df = df[df['gate'].isin(top_gates)]

    gate_order = df['gate'].value_counts().loc[top_gates].index.tolist()


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
    Plots a bar chart of the average number of gates occupied per hour.

    Parameters:
    - avg_hourly: DataFrame with 'hour' (as datetime.time or int) and 'avg_occupied_gates'
    - max_capacity: optional horizontal line indicating maximum gate capacity
    - from_hour: first hour to include (default: 1)
    - to_hour: last hour to include (default: 22)
    """
    import matplotlib.pyplot as plt

    # Convert hour to integer
    avg_hourly['hour_int'] = avg_hourly['hour'].apply(lambda t: t.hour if hasattr(t, 'hour') else int(t))

    # Filter range
    df_filtered = avg_hourly[(avg_hourly['hour_int'] >= from_hour) & (avg_hourly['hour_int'] <= to_hour)]

    x = list(range(len(df_filtered)))
    y = df_filtered['avg_occupied_gates']
    hour_labels = [h.strftime('%H:%M') for h in df_filtered['hour']]

    # Plot
    plt.figure(figsize=(14, 6))
    bars = plt.bar(x, y, color='#4C78A8', edgecolor='grey', linewidth=3, alpha=0.9, label='Average occupied gates')

    for i, val in enumerate(y):
        plt.text(i, math.ceil(val), f"{math.ceil(val)}", ha='center', va='bottom', fontsize=10)

    if max_capacity:
        plt.axhline(y=max_capacity, color='#444444', linestyle='--', linewidth=1.5, label='Max gate capacity')

    plt.xticks(ticks=x, labels=hour_labels, rotation=45)
    plt.ylabel('Average Gates Occupied', fontsize=12)
    plt.legend()
    
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_axisbelow(True)
    ax.grid(True, axis='y', linestyle='--', alpha=0.7)

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


def plot_gate_occupancy_comparison(folder_path, top_n=15):
    """
    Plots a comparison between median occupancy per operation and average total daily occupancy per gate.

    Parameters:
    - folder_path: str. Path to the folder containing the daily GateOccupancy*.csv files.
    - top_n: int. Number of top gates to display (based on number of operations).
    """
    csv_files = glob.glob(os.path.join(folder_path, "GateOccupancy*.csv"))
    df_all = []

    for file in csv_files:
        df = pd.read_csv(file)
        df['date'] = os.path.basename(file)[-6:-4]  # Extracts day from filename (e.g., 20 from GateOccupancy20.csv)
        df_all.append(df)

    df_all = pd.concat(df_all, ignore_index=True)
    df_all['gate'] = df_all['gate'].astype(str)

    # Median duration per operation
    median_per_op = df_all.groupby('gate')['duration_minutes'].median().rename('median_op')

    # Mean daily total duration
    total_per_day = df_all.groupby(['date', 'gate'])['duration_minutes'].sum().reset_index()
    mean_daily_total = total_per_day.groupby('gate')['duration_minutes'].mean().rename('mean_daily_total')

    # Combine results
    summary = pd.concat([median_per_op, mean_daily_total], axis=1).dropna()

    # Select top N gates
    top_gates = df_all['gate'].value_counts().head(top_n).index
    summary = summary.loc[summary.index.isin(top_gates)]

    # Sort by mean daily total
    summary = summary.sort_values(by='mean_daily_total', ascending=False)

    # 📊 Plot
    x = np.arange(len(summary))
    width = 0.35

    plt.figure(figsize=(14, 6))
    plt.bar(x, summary['mean_daily_total'], label='Mean total per day', color='#7fbfff', alpha=0.6, edgecolor='grey')
    plt.bar(x, summary['median_op'], label='Median per operation', color='#1b2a38', alpha=0.8, edgecolor='grey')
    
    ax = plt.gca()
    ax.set_axisbelow(True)
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    for i, gate in enumerate(summary.index):
        plt.text(i, summary['median_op'][i] + 5,      
             f"{summary['median_op'][i]:.0f}", 
             ha='center', color='black', fontsize=9)
    
        plt.text(i, summary['mean_daily_total'][i] + 5,
             f"{summary['mean_daily_total'][i]:.0f}", 
             ha='center', color='black', fontsize=9)
    
    plt.xticks(ticks=x, labels=summary.index, rotation=0)
    plt.ylabel("Duration (minutes)", fontsize=12)
    plt.xlabel("Gates", fontsize=12)
    plt.legend(fontsize=12)
    plt.tight_layout()
    plt.show()
    
    
    
    
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import glob

def plot_gate_occupancy_comparison_peak_hours(folder_path, top_n=15, fixed_gates=None, show_total_bar=True):
    """
    Plots gate occupancy comparison (median per operation and mean total per day) for 12:00–14:00 period.

    Parameters:
    - folder_path: str. Path to folder with GateOccupancy*.csv files.
    - top_n: int. Number of top gates to show (ignored if fixed_gates is used).
    - fixed_gates: list of gate labels (str) to fix which gates to display, useful for consistent comparisons.
    - show_total_bar: bool. If True, plots mean daily total bar; otherwise shows only median per operation.
    """
    csv_files = glob.glob(os.path.join(folder_path, "GateOccupancy*.csv"))
    df_all = []

    for file in csv_files:
        df = pd.read_csv(file)
        df['date'] = os.path.basename(file)[-6:-4]  # Extract day from filename
        df['start_time'] = pd.to_datetime(df['start_time'])  # Auto-parse datetime
        # Filter: only keep operations starting between 12:00 and 14:00
        df = df[
            ((df['start_time'].dt.hour >= 6) & (df['start_time'].dt.hour < 7)) |
            ((df['start_time'].dt.hour >= 12) & (df['start_time'].dt.hour < 13))
        ]
        df_all.append(df)

    df_all = pd.concat(df_all, ignore_index=True)
    df_all['gate'] = df_all['gate'].astype(str)

    # Calculate KPIs
    median_per_op = df_all.groupby('gate')['duration_minutes'].median().rename('median_op')

    total_per_day = df_all.groupby(['date', 'gate'])['duration_minutes'].sum().reset_index()
    mean_daily_total = total_per_day.groupby('gate')['duration_minutes'].mean().rename('mean_daily_total')

    # Merge
    summary = pd.concat([median_per_op, mean_daily_total], axis=1).dropna()

    # Filter gates
    if fixed_gates is not None:
        summary = summary.loc[summary.index.isin(fixed_gates)]
        summary = summary.reindex([g for g in fixed_gates if g in summary.index])
    else:
        top_gates = df_all['gate'].value_counts().head(top_n).index
        summary = summary.loc[summary.index.isin(top_gates)]
        summary = summary.sort_values(by='mean_daily_total', ascending=False)

    # Plot
    x = np.arange(len(summary))
    plt.figure(figsize=(14, 6))

    if show_total_bar:
        plt.bar(x, summary['mean_daily_total'], label='Mean total per day (12–14h)',
                color='#7fbfff', alpha=0.6, edgecolor='grey')
    plt.bar(x, summary['median_op'], label='Median per operation (6–7h) / (12–13h)',
            color='#1b2a38', alpha=0.9, edgecolor='grey')

    ax = plt.gca()
    ax.set_axisbelow(True)
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    for i, gate in enumerate(summary.index):
        plt.text(i, summary['median_op'][i] + 5,
                 f"{summary['median_op'][i]:.0f}", ha='center', color='black', fontsize=9, fontweight='bold')
        if show_total_bar:
            plt.text(i, summary['mean_daily_total'][i] + 5,
                     f"{summary['mean_daily_total'][i]:.0f}", ha='center', color='black', fontsize=9)

    plt.xticks(ticks=x, labels=summary.index, rotation=0)
    plt.ylabel("Duration (minutes)", fontsize=12)
    plt.xlabel("Gates", fontsize=12)
    plt.legend(fontsize=12)
    plt.tight_layout()
    plt.show()
    
folder_path = r"C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\October\GateOccupancy"
    
fixed_gates = ['83', '86', '90', '81', '141', '140', '19', '76', '84', '89', '14', '85', '16', '17', '18']

plot_gate_occupancy_comparison_peak_hours(folder_path, fixed_gates=fixed_gates, show_total_bar=False)
