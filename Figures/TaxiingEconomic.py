import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.nonparametric.smoothers_lowess import lowess

# === PARAMETERS ===
fuel_rate_per_engine = 0.135             # kg/s per engine
engines = 2                              # typical twin-engine aircraft
fuel_rate_total = fuel_rate_per_engine * engines  # total fuel flow (kg/s)
cost_per_kg = 1.165                      # €/kg of Jet A-1

# Define custom colors for each runway
colors = {'1': '#7fbfff', '2': '#3e5c76', '3': '#bdbdbd'}

# === LOAD DATA ===
# Load all CSV files containing hourly taxiing statistics
base_path = r"C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\October\TaxiingTime"
file_pattern = os.path.join(base_path, "taxiing_hourly_stats*.csv")
files = glob.glob(file_pattern)

# Concatenate all files into a single DataFrame
df_all = pd.concat((pd.read_csv(f) for f in files), ignore_index=True)

# Filter to remove unrealistic taxiing times
df_all = df_all[df_all['median_taxi_time'].between(20, 900)]
df_all['used_runway'] = df_all['used_runway'].astype(str).str.strip()

# === PLOT SETUP: 2 SUBPLOTS ===
fig, (ax_fuel, ax_cost) = plt.subplots(2, 1, sharex=True, figsize=(14, 8))

# Define traffic zones to be shaded
off_peak = (10, 25)    # low traffic range
on_peak  = (30, 45)    # high traffic range
off_color = 'lightsteelblue'
on_color  = 'dimgray'

# Shade traffic zones in both plots
for ax in (ax_fuel, ax_cost):
    ax.axvspan(off_peak[0], off_peak[1], color=off_color, alpha=0.3, label='Off-peak zone')
    ax.axvspan(on_peak[0],  on_peak[1],  color=on_color,  alpha=0.3, label='On-peak zone')

# === MAIN PLOTTING LOOP ===
for runway, df_rwy in df_all.groupby('used_runway'):
    # Group by number of operations and calculate mean taxi time
    df_grp = (
        df_rwy
        .groupby('total_operations')
        .agg(avg_taxiing_time=('median_taxi_time','mean'))
        .reset_index()
        .sort_values('total_operations')
    )

    # Compute per-aircraft fuel and cost
    x = df_grp['total_operations'].values
    y_fuel = df_grp['avg_taxiing_time'].values * fuel_rate_total
    y_cost = y_fuel * cost_per_kg

    # Skip runways with too few data points
    if len(x) < 5:
        continue

    # Smooth both curves using LOWESS
    color = colors.get(runway, '#666666')
    sf = lowess(y_fuel, x, frac=0.2)
    sc = lowess(y_cost, x, frac=0.2)

    # Plot fuel consumption curve
    ax_fuel.plot(
        sf[:,0], sf[:,1],
        label=f'Fuel – RWY {runway}',
        color=color, linewidth=2.5, zorder=3
    )

    # Plot economic cost curve
    ax_cost.plot(
        sc[:,0], sc[:,1],
        label=f'Cost – RWY {runway}',
        color=color, linestyle='--', linewidth=2.5, zorder=3
    )

# === FUEL PLOT FORMATTING ===
ax_fuel.set_ylabel('Fuel consumption/aircraft (kg)', fontsize=12)
ax_fuel.set_ylim(0, 160)
ax_fuel.grid(True, linestyle='--', alpha=0.7)

# Remove duplicate zone labels from legend
handles_f, labels_f = ax_fuel.get_legend_handles_labels()
unique = dict(zip(labels_f, handles_f))
ax_fuel.legend(unique.values(), unique.keys(), loc='upper left', fontsize=10)

# === COST PLOT FORMATTING ===
ax_cost.set_xlabel('Operations/h', fontsize=12)
ax_cost.set_ylabel('Cost/aircraft (€)', fontsize=12)
ax_cost.set_ylim(0, 160 * cost_per_kg)
ax_cost.grid(True, linestyle='--', alpha=0.7)

# Remove duplicate zone labels from legend
handles_c, labels_c = ax_cost.get_legend_handles_labels()
unique = dict(zip(labels_c, handles_c))
ax_cost.legend(unique.values(), unique.keys(), loc='upper left', fontsize=10)

plt.tight_layout()
plt.show()
