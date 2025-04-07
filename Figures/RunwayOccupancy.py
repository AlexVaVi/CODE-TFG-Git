import matplotlib.pyplot as plt
import pandas as pd
df_usage = pd.read_csv("runway_usage_stats.csv") 
    
# Agrupar per runway i nombre d’operacions actives
grouped = df_usage.groupby(['used_runway', 'active_operations'])['runway_time'].mean().reset_index()

# Paleta de colors
colors = {1: '#2c3e50', 2: '#4b6eaf', 3: '#95a5a6'}

plt.figure(figsize=(10, 6))

# Per a cada runway, fem la seva corba
for rwy in sorted(df_usage['used_runway'].unique()):
    df_rwy = grouped[grouped['used_runway'] == rwy]
    plt.plot(df_rwy['active_operations'], df_rwy['runway_time'], marker='o',
             label=f'Runway {rwy}', color=colors.get(rwy, '#333333'))

plt.xlabel("Active operations")
plt.ylabel("Average runway occupancy time (s)")
plt.title("Runway occupancy vs Active operations")
plt.grid(True)
plt.legend(title="Runway")
plt.tight_layout()
plt.show()
