import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import numpy as np
import os

# === DATA DEFINITION ===

airlines = ['SAS', 'NSZ', 'RYR', 'DLH', 'FIN']
runways = ['Runway 1', 'Runway 2', 'Runway 3']
flights = {
    'SAS': [434, 311, 351],
    'NSZ': [149, 94, 114],
    'RYR': [78, 47, 72],
    'DLH': [34, 25, 28],
    'FIN': [36, 25, 27]
}

# Parameters for cost estimation
fuel_burn_per_sec = 0.125 * 2  # kg/s (two engines)
extra_seconds = {'Runway 1': 33.8, 'Runway 2': 49.9, 'Runway 3': 15.4}  # average additional time per flight
eur_per_kg = 1.165  # Jet A-1 cost per kg in €

# === COST COMPUTATION ===

weekly_costs, annual_costs = [], []

for airline in airlines:
    w, a = [], []
    for i, runway in enumerate(runways):
        n = flights[airline][i]
        extra_fuel = n * fuel_burn_per_sec * extra_seconds[runway]
        cost_w = extra_fuel * eur_per_kg  # weekly cost
        w.append(cost_w)
        a.append(cost_w * 52)  # annual cost
    weekly_costs.append(w)
    annual_costs.append(a)

# === PLOTTING ===

bar_height = 0.4
index = np.arange(len(airlines))
colors = ['#7fbfff', '#3e5c76', '#bdbdbd']
alpha = 1

fig, ax = plt.subplots(figsize=(6, 6))

# Stack bars for each airline with different runway contributions
labels_added = set()
for j, airline in enumerate(airlines):
    items = list(zip(weekly_costs[j], colors, runways))
    items.sort(reverse=True)  # plot larger bars first for clarity
    for cost, color, label in items:
        show_label = label if label not in labels_added else None
        ax.barh(index[j], cost, height=bar_height, color=color, edgecolor='black', label=show_label)
        labels_added.add(label)

# === ADD AIRLINE LOGOS NEXT TO BARS ===

for i, airline in enumerate(airlines):
    logo_path = f'{airline}.png'
    if os.path.isfile(logo_path):
        logo = plt.imread(logo_path)
        im = OffsetImage(logo, zoom=0.02)
        ab = AnnotationBbox(im, xy=(-0.01, index[i] - 0.3), xycoords=('axes fraction', 'data'),
                            box_alignment=(1, 0.5), frameon=False)
        ax.add_artist(ab)

# === STYLING ===

ax.set_axisbelow(True)
ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

ax.set_yticks(index)
ax.set_yticklabels(airlines, fontsize=12)
ax.invert_yaxis()
ax.set_xlabel("Weekly Operational Cost (k€)", fontsize=12)
ax.grid(True, axis='x', linestyle='--', alpha=0.5)

# === ADD WEEKLY AND ANNUAL TOTAL COSTS PER AIRLINE ===

for i, (week, year) in enumerate(zip(weekly_costs, annual_costs)):
    total_week = sum(week)
    total_year = sum(year)

    ax.text(100, index[i] - 0.3, f"Weekly: {total_week:.0f}€",
            va='bottom', ha='left', fontsize=9, color='black')
    ax.text(100, index[i] - 0.5, f"Annual: {total_year:.0f}€",
            va='bottom', ha='left', fontsize=9, color='gray')

plt.tight_layout()
plt.legend()
plt.show()

