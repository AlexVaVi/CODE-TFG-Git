# import pandas as pd
# import os
# import glob
# from datetime import timedelta
# from HotspotsMethod2 import hotspots2
# from shapely.geometry import LineString

# === CONFIGURATION ===
# csv_dir = r"C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\October"
# df_airport = pd.read_csv(r'C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\arlanda_airport_nodes.csv')
# df_airport = df_airport[df_airport['type'] == 'runway']
# pattern = os.path.join(csv_dir, "Oct24_*_00am_24pm_All_ProcessedData.csv")
# csv_files = sorted(glob.glob(pattern))
# hours_to_check = list(range(5, 22))
# levels = [3, 4, 5]

# === BUILD RUNWAY LINESTRINGS ===
# runway_lines = []
# for rwy_id in df_airport['way_id'].unique():
#     rwy_points = df_airport[df_airport['way_id'] == rwy_id].sort_values(by='node_id')
#     coords = list(zip(rwy_points['longitude'], rwy_points['latitude']))
#     if len(coords) >= 2:
#         runway_lines.append(LineString(coords))

# === INITIALIZE RESULTS STRUCTURE ===
# columns = pd.MultiIndex.from_product([[f"Day{i+1}" for i in range(len(csv_files))], levels], names=["Day", "Level"])
# hourly_counts = pd.DataFrame(0, index=hours_to_check, columns=columns)

# === PROCESS EACH DAY FILE ===
# for idx, file in enumerate(csv_files):
#     print(f"📂 Processing {file}")
#     df = pd.read_csv(file)
#     df['timestamp'] = pd.to_datetime(df['timestamp'])
#     day_start = df['timestamp'].min().replace(minute=0, second=0, microsecond=0)

#     for hour in hours_to_check:
#         start_time = day_start + timedelta(hours=hour)
#         end_time = start_time + timedelta(hours=1)
#         df_hot = hotspots2(df, runway_lines, start_time=start_time, end_time=end_time)

#         for lvl in levels:
#             count = len(df_hot[df_hot['level'] == lvl])
#             hourly_counts.loc[hour, (f"Day{idx+1}", lvl)] = count

#         total = sum(hourly_counts.loc[hour, (f"Day{idx+1}", lvl)] for lvl in levels)
#         print(f"🕐 {os.path.basename(file)} {start_time.strftime('%H:%M')} → {total} hotspot(s) (levels 3–5)")

# === CALCULATE HOURLY AVERAGES ===
# mean_cols = pd.MultiIndex.from_product([["Mean"], levels])
# mean_df = pd.DataFrame(index=hours_to_check, columns=mean_cols)
# for lvl in levels:
#     lvl_data = hourly_counts.xs(lvl, axis=1, level="Level")
#     mean_df[("Mean", lvl)] = lvl_data.mean(axis=1)

# === COMBINE AND EXPORT ===
# hourly_counts_final = pd.concat([hourly_counts, mean_df], axis=1)
# hourly_counts_final.insert(0, "Hour", [f"{h:02d}:00" for h in hours_to_check])
# output_path = os.path.join(csv_dir, "hotspot2_hourly_mean_levels_separated.csv")
# hourly_counts_final.to_csv(output_path, index=False)
# print(f"✅ Results saved to: {output_path}")


import matplotlib.pyplot as plt
import numpy as np

# === TIME INTERVALS AND HOTSPOT LEVEL MEANS ===

time_labels = [
    "05–06", "06–07", "07–08", "08–09", "09–10", "10–11", "11–12",
    "12–13", "13–14", "14–15", "15–16", "16–17", "17–18", "18–19",
    "19–20", "20–21", "21–22"
]

lvl3 = np.array([21.5, 23.375, 16.25, 9.5, 9.5, 11, 8.5, 19.625, 12.625, 14, 14.25, 12.125, 8, 8, 10, 4.5, 0.875])
lvl4 = np.array([8.75, 7.5, 2.75, 2.75, 3, 2.75, 1.875, 5, 4.125, 4, 4, 2.375, 2.375, 2.25, 1.75, 1, 0.25])
lvl5 = np.array([3.625, 7.375, 2.25, 0.875, 0.375, 0.5, 1.375, 5, 1.875, 2, 1, 2.875, 0.625, 0.5, 1.375, 0.25, 0])

x = np.arange(len(time_labels))
colors = {3: '#7fbfff', 4: '#1b2a38', 5: '#bdbdbd'}

# === CUMULATIVE BASES FOR STACKED AREAS ===
base3 = lvl3
base4 = base3 + lvl4
base5 = base4 + lvl5

# === PLOT AREA CHART ===

plt.figure(figsize=(14, 6))

# Level 3
plt.plot(time_labels, base3, marker='o', color=colors[3], linewidth=2)
plt.fill_between(time_labels, 0, base3, color=colors[3], alpha=0.4, label="Level 3")
for i, val in enumerate(lvl3):
    plt.text(i, val / 2, f"{val:.0f}", ha='center', va='center', fontsize=9, color='black')

# Level 4
plt.plot(time_labels, base4, marker='o', color=colors[4], linewidth=2)
plt.fill_between(time_labels, base3, base4, color=colors[4], alpha=0.4, label="Level 4")
for i, val in enumerate(lvl4):
    plt.text(i, base3[i] + val / 2, f"{val:.0f}", ha='center', va='center', fontsize=9, color='white')

# Level 5
plt.plot(time_labels, base5, marker='o', color=colors[5], linewidth=2)
plt.fill_between(time_labels, base4, base5, color=colors[5], alpha=0.4, label="Level 5")
for i, val in enumerate(lvl5):
    if val > 0:
        plt.text(i, base5[i] + 1.2, f"{val:.0f}", ha='center', va='bottom', fontsize=9, color='black')

# === AXIS, LEGEND AND STYLE ===

ax = plt.gca()
ax.set_axisbelow(True)
ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.ylabel("Average Number of Total Hotspots", fontsize=12)
plt.xticks(rotation=45)
plt.legend(title="Hotspot Level", loc='upper right', fontsize=10)
plt.tight_layout()
plt.show()
