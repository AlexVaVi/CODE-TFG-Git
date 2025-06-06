import matplotlib.pyplot as plt
import numpy as np

# === DAILY FLIGHT DATA (replace with your real values if needed) ===

days = ['Oct 20', 'Oct 21', 'Oct 22', 'Oct 23', 'Oct 24', 'Oct 25', 'Oct 26', 'Oct 27']
opensky = [488, 573, 576, 599, 589, 601, 430, 487]         # Post-processed OpenSky data
flightradar = [590, 618, 623, 632, 632, 623, 440, 539]     # Reference values from FlightRadar24

x = np.arange(len(days))
width = 0.3

# === PLOT CONFIGURATION ===

fig, ax = plt.subplots(figsize=(12, 6))

# Plot both datasets as grouped bars
rects1 = ax.bar(x - width/2, opensky, width, label='OpenSky (Post-Processed)', 
                color='#444444', edgecolor='none')
rects2 = ax.bar(x + width/2, flightradar, width, label='FlightRadar24', 
                color='#4C78A8', edgecolor='none')

# === AXES AND LABELS ===

ax.set_ylabel('Number of Flights', fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(days, fontsize=12)
ax.tick_params(axis='y', labelsize=12)
ax.set_axisbelow(True)

# Clean background
ax.set_facecolor('white')
fig.patch.set_facecolor('white')

# === LEGEND ===

ax.legend(fontsize=12, loc='upper right', frameon=False)

# === ADD NUMERIC LABELS ABOVE BARS ===

for bars in [rects1, rects2]:
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5),  # offset above bar
                    textcoords='offset points',
                    ha='center', va='bottom',
                    fontsize=10)

# === LAYOUT AND EXPORT ===

plt.tight_layout()
plt.subplots_adjust(top=1.0)
plt.savefig('flight_comparison_clean.png', bbox_inches='tight', dpi=300)
plt.show()

