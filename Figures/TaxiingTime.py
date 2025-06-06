import glob
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from statsmodels.nonparametric.smoothers_lowess import lowess

# === LOAD ALL HOURLY TAXIING STATS FILES ===
base_path = r"C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\October\TaxiingTime"
file_pattern = os.path.join(base_path, "taxiing_hourly_stats*.csv")
files = glob.glob(file_pattern)

# Concatenate all CSVs into a single DataFrame
df_list = [pd.read_csv(f) for f in files]
df_all = pd.concat(df_list, ignore_index=True)

# Filter for reasonable taxiing times
df_all = df_all[df_all['median_taxi_time'].between(20, 900)]
df_all['used_runway'] = df_all['used_runway'].astype(str).str.strip()

# Color palette for each runway
colors = {
    '1': '#7fbfff',
    '2': '#3e5c76',
    '3': '#bdbdbd',
}

# === PLOT SETUP ===
plt.figure(figsize=(14, 6))

# === PROCESS DATA BY RUNWAY ===
for runway, df_rwy in df_all.groupby('used_runway'):
    # Aggregate by number of operations per hour
    df_rwy_grouped = (
        df_rwy.groupby('total_operations')
        .agg(
            avg_taxiing_time=('median_taxi_time', 'mean'),
            min_taxiing_time=('median_taxi_time', 'min'),
            max_taxiing_time=('median_taxi_time', 'max')
        )
        .reset_index()
        .sort_values('total_operations')
    )

    x = df_rwy_grouped['total_operations'].values
    y = df_rwy_grouped['avg_taxiing_time'].values
    ymin = df_rwy_grouped['min_taxiing_time'].values
    ymax = df_rwy_grouped['max_taxiing_time'].values

    # Skip if too few points
    if len(x) >= 5:
        color = colors.get(runway, '#666666')

        # LOWESS smoothing on the mean curve
        smoothed_mean = lowess(y, x, frac=0.2)
        x_smooth, y_smooth = smoothed_mean[:, 0], smoothed_mean[:, 1]

        # Compute means within defined traffic zones
        mask_10_25 = (x_smooth >= 10) & (x_smooth <= 25)
        mask_30_45 = (x_smooth >= 30) & (x_smooth <= 45)
        mean_10_25 = np.mean(y_smooth[mask_10_25]) if np.any(mask_10_25) else None
        mean_30_45 = np.mean(y_smooth[mask_30_45]) if np.any(mask_30_45) else None

        print(f"✈️ Runway {runway} → Mean taxiing time [10-25 op/h]: {mean_10_25:.1f}s")
        print(f"✈️ Runway {runway} → Mean taxiing time [30-45 op/h]: {mean_30_45:.1f}s")

        # Interpolate min/max for smoothed X values (optional shaded band)
        lower_interp = np.interp(x_smooth, x, ymin)
        upper_interp = np.interp(x_smooth, x, ymax)
        # Uncomment to show min-max envelope:
        # plt.fill_between(x_smooth, lower_interp, upper_interp, color=color, alpha=0.2)

        # Raw scatter points (mean per bin)
        plt.scatter(
            x, y,
            s=30, alpha=0.4, color=color, edgecolor='white', linewidth=0.5,
        )

        # Smoothed average line
        plt.plot(x_smooth, y_smooth, label=f'Runway {runway}', linewidth=3, color=color)

        # Highlight min and max of the smoothed curve
        smooth_min = np.min(y_smooth)
        smooth_max = np.max(y_smooth)

    # === DRAW MIN/MAX LINES WITH ANNOTATIONS ===
    if runway == '1':
        # Place labels on the right
        plt.axhline(smooth_min, linestyle='--', linewidth=1, color=color, alpha=0.7)
        plt.text(x.max(), smooth_min + 20, f'Min {smooth_min:.0f}s',
                 va='top', ha='right', fontsize=9, color=color)

        plt.axhline(smooth_max, linestyle='--', linewidth=1, color=color, alpha=0.7)
        plt.text(x.max(), smooth_max + 20, f'Max {smooth_max:.0f}s',
                 va='top', ha='right', fontsize=9, color=color)
    else:
        # Place labels on the left
        plt.axhline(smooth_min, linestyle='--', linewidth=1, color=color, alpha=0.7)
        plt.text(2, smooth_min + 20, f'Min {smooth_min:.0f}s',
                 va='top', ha='left', fontsize=9, color=color)

        plt.axhline(smooth_max, linestyle='--', linewidth=1, color=color, alpha=0.7)
        plt.text(2, smooth_max + 20, f'Max {smooth_max:.0f}s',
                 va='top', ha='left', fontsize=9, color=color)

# === FINAL FORMATTING ===
ax = plt.gca()
ax.set_axisbelow(True)
ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.xlabel('Number of operations per hour', fontsize=12)
plt.ylabel('Taxiing time (s)', fontsize=12)
plt.ylim(0, 600)
plt.xlim(left=0)
plt.yticks(np.arange(0, 601, 100))
plt.legend(fontsize=10)
plt.tight_layout()
plt.show()
