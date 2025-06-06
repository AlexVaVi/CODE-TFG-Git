import matplotlib.pyplot as plt

# === TIME SLOTS AND CORRESPONDING AVERAGE HOTSPOT VALUES ===

time_slots = [
    "05–06", "06–07", "07–08", "08–09", "09–10", "10–11", "11–12",
    "12–13", "13–14", "14–15", "15–16", "16–17", "17–18", "18–19",
    "19–20", "20–21", "21–22"
]
avg_hotspots = [
    16, 34, 30, 11.00, 17.86, 11.14, 22.43,
    27.57, 15.75, 14.57, 11.86, 18.57, 9.63, 8.29,
    12.86, 23.71, 5.75
]

# === CREATE AREA PLOT ===

plt.figure(figsize=(14, 6))
plt.plot(time_slots, avg_hotspots, marker='o', color='#1b2a38', linewidth=2)
plt.fill_between(time_slots, avg_hotspots, color='#7fbfff', alpha=0.4)

# === ADD VALUES ABOVE EACH POINT ===

for i, val in enumerate(avg_hotspots):
    plt.text(i, val + 0.5, f"{val:.0f}", ha='center', va='bottom', fontsize=9, fontweight='bold')

# === AXIS AND STYLING ===

ax = plt.gca()
ax.set_axisbelow(True)
ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.ylabel("Average Number of Hotspots", fontsize=12)
plt.xticks(rotation=45, fontsize=11)
plt.yticks(fontsize=11)
plt.tight_layout()
plt.show()
