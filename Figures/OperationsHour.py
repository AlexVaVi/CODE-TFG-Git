import pandas as pd
import glob
import os

# === LOAD FILES ===

folder_path = r'C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\October\RunwayUsage'
file_pattern = os.path.join(folder_path, 'runway_hourly_stats*.csv')
files = glob.glob(file_pattern)

# Concatenate all CSV files
df_all = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)

# Convert 'hour' column to datetime
df_all['hour'] = pd.to_datetime(df_all['hour'])

# Extract only the hour (0–23)
df_all['hour_of_day'] = df_all['hour'].dt.hour

# Drop duplicate rows by hour (multiple rows per hour due to runway breakdown)
df_unique = df_all.drop_duplicates(subset=['hour'])

# === GROUP AND AVERAGE ===

# Compute mean total operations per hour across all days
ops_per_hour = (
    df_unique.groupby('hour_of_day')['total_operations']
    .mean()
    .reset_index(name='mean_ops')
)

# Format hour intervals as strings
ops_per_hour['time_interval'] = ops_per_hour['hour_of_day'].apply(
    lambda h: f"{h:02d}:00 - {h+1:02d}:00" if h < 23 else "23:00 - 00:00"
)

# Final column order
ops_per_hour = ops_per_hour[['time_interval', 'mean_ops']]

# Display result
print(ops_per_hour)




