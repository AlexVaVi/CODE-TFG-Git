import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from statsmodels.nonparametric.smoothers_lowess import lowess

# === INPUT FILES ===
files = [
    r"C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\October\RunwayUsage\runway_hourly_stats20.csv",
    r"C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\October\RunwayUsage\runway_hourly_stats21.csv",
    r"C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\October\RunwayUsage\runway_hourly_stats22.csv",
    r"C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\October\RunwayUsage\runway_hourly_stats23.csv",
    r"C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\October\RunwayUsage\runway_hourly_stats24.csv",
    r"C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\October\RunwayUsage\runway_hourly_stats25.csv",
    r"C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\October\RunwayUsage\runway_hourly_stats26.csv",
    r"C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\October\RunwayUsage\runway_hourly_stats27.csv"
]

# === LOAD AND CLEAN DATA ===
df_list = [pd.read_csv(f) for f in files]
df_all = pd.concat(df_list, ignore_index=True)

# Filter out unrealistic runway time values
df_all = df_all[df_all['median_runway_time'].between(10, 160)]

# Ensure runway IDs are string and clean
df_all['used_runway'] = df_all['used_runway'].astype(str).str.strip()

# Custom color per runway
colors = {
    '1': '#7fbfff',
    '2': '#3e5c76',
    '3': '#bdbdbd',
}

# === PLOT ===
plt.figure(figsize=(14, 6))

for runway, df_rwy in df_all.groupby('used_runway'):
    # Group by number of ops/hour and compute mean runway time
    df_rwy_grouped = (
        df_rwy.groupby('total_operations')
        .agg(avg_runway_time=('median_runway_time', 'mean'))
        .reset_index()
        .sort_values('total_operations')
    )

    x = df_rwy_grouped['total_operations'].values
    y = df_rwy_grouped['avg_runway_time'].values

    if len(x) >= 5:
        smoothed = lowess(y, x, frac=0.2)
        x_smooth, y_smooth = smoothed[:, 0], smoothed[:, 1]

        color = colors.get(runway, '#666666')
        plt.plot(x_smooth, y_smooth, label=f'Runway {runway}', linewidth=3, color=color)

        # Dashed lines for min/max of the smoothed curve
        smooth_min = np.min(y_smooth)
        smooth_max = np.max(y_smooth)

        plt.axhline(smooth_min, linestyle='--', linewidth=1, color=color, alpha=0.7)
        plt.axhline(smooth_max, linestyle='--', linewidth=1, color=color, alpha=0.7)

        # Scatter original means for context
        plt.scatter(
            x, y,
            s=30, alpha=0.4, color=color,
            edgecolor='white', linewidth=0.5,
        )

        # Annotate min/max with adaptive alignment
        if runway == '3':
            plt.text(
                x_smooth.max(), smooth_min + 2, f'Min {smooth_min:.0f}s',
                va='bottom', ha='right', fontsize=9, color=color
            )
            plt.text(
                x_smooth.max(), smooth_max + 2, f'Max {smooth_max:.0f}s',
                va='bottom', ha='right', fontsize=9, color=color
            )
        else:
            plt.text(
                2, smooth_min + 2, f'Min {smooth_min:.0f}s',
                va='bottom', ha='left', fontsize=9, color=color
            )
            plt.text(
                2, smooth_max + 2, f'Max {smooth_max:.0f}s',
                va='bottom', ha='left', fontsize=9, color=color
            )

# === DEBUG INFO ===
print("Max value in total_operations:", df_all['total_operations'].max())
print("Sorted unique values:", sorted(df_all['total_operations'].unique()))

# === AXIS AND STYLE ===
ax = plt.gca()
ax.set_axisbelow(True)
ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.xlabel('Number of operations per hour', fontsize=12)
plt.ylabel('Runway time (s)', fontsize=12)
plt.ylim(0, 70)
plt.yticks(np.arange(0, 71, 10))
plt.xlim(left=0)
plt.legend(fontsize=10)
plt.tight_layout()
plt.show()



