import pandas as pd
import os
import glob
from collections import defaultdict, Counter

# === CONFIGURATION ===
days = range(20, 28)  # October 20th to 27th
folder_gt = r"C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\October\GroundTime"
folder_flight = r"C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\October"

# 1️⃣ Count total number of operations per hour (all runways, all days)
ops_per_hour = defaultdict(int)
gt_files = glob.glob(os.path.join(folder_gt, "groundtime_stats*.csv"))

for file in gt_files:
    df = pd.read_csv(file)
    df['t_start'] = pd.to_datetime(df['t_start'])
    df['hour_slot'] = df['t_start'].dt.floor('h')  # Round to the nearest hour
    counts = df.groupby('hour_slot').size()
    for time, count in counts.items():
        ops_per_hour[time] += count  # Global hourly operation count

# 2️⃣ Initialize structure to store callsign prefixes per runway
prefixes_by_runway = defaultdict(list)

# 3️⃣ Iterate over each day to associate callsigns with runways during peak load
for day in days:
    try:
        # Load corresponding ground time and processed flight files
        gt_path = os.path.join(folder_gt, f"groundtime_stats{day}.csv")
        fl_path = os.path.join(folder_flight, f"Oct24_{day}_00am_24pm_All_ProcessedData.csv")

        df_gt = pd.read_csv(gt_path)
        df_flight = pd.read_csv(fl_path)

        df_gt['t_start'] = pd.to_datetime(df_gt['t_start'])
        df_gt['hour_slot'] = df_gt['t_start'].dt.floor('h')

        for _, row in df_gt.iterrows():
            hour = row['hour_slot']

            # Only consider hours with 30 to 45 total operations (moderate-high traffic)
            if not (30 <= ops_per_hour[hour] <= 45):
                continue

            callsign_nr = row['callsign']
            runway = str(row['used_runway'])

            # Retrieve original callsign from processed flight data
            match = df_flight[df_flight['callsign_group'] == callsign_nr]
            if match.empty:
                continue

            callsign = str(match.iloc[0]['callsign'])
            if len(callsign) >= 3:
                prefix = callsign[:3]  # Airline identifier
                prefixes_by_runway[runway].append(prefix)

    except Exception as e:
        print(f"⚠️ Error while processing day {day}: {e}")

# 4️⃣ Final summary: top 3 airline prefixes per runway
print("\n📊 Top 3 airlines per runway (when operations/hour were between 30–45):")
for runway in sorted(prefixes_by_runway):
    counter = Counter(prefixes_by_runway[runway])
    top3 = counter.most_common(3)
    print(f"  Runway {runway}:")
    for prefix, count in top3:
        print(f"    • {prefix}: {count} flights")


