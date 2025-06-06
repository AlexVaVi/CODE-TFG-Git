import pandas as pd
import os
from collections import Counter

# === Configuration ===
days = range(20, 28)  # Analyze flight data from October 20th to 27th
path_flightdata = r"C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\October"

# Initialize a counter for airline prefixes (first 3 letters of callsigns)
prefix_counter = Counter()

# === Process each day's flight data ===
for day in days:
    try:
        # Build the file path for the given day
        fl_path = os.path.join(path_flightdata, f"Oct24_{day}_00am_24pm_All_ProcessedData.csv")
        print(f"📁 Reading: {fl_path}")
        
        # Read the CSV
        df_flight = pd.read_csv(fl_path)
        df_flight['callsign'] = df_flight['callsign'].astype(str)

        # Get one entry per unique callsign_group (i.e., one row per flight)
        df_unique = df_flight.drop_duplicates(subset=['callsign_group'])

        # Extract the airline prefix (first 3 characters of the callsign)
        for cs in df_unique['callsign']:
            if isinstance(cs, str) and len(cs) >= 3:
                prefix = cs[:3]
                prefix_counter[prefix] += 1

    except Exception as e:
        print(f"❌ Error while loading data for day {day}: {e}")

# === Display top 10 most frequent airline prefixes ===
print("\n📊 Top 10 most frequent airlines (by callsign prefix):")
for prefix, count in prefix_counter.most_common(10):
    print(f"  {prefix}: {count} flights")
