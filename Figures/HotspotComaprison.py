import matplotlib.pyplot as plt

# === HOTSPOT POSITIONS ON X-AXIS ===

x_pos = [1, 2, 3]  # Custom X positions for H1, H2, H3

# === DATA ===

groups = ['H1', 'H2', 'H3']
means = [293, 465, 125]           # Mean taxi time during peak period
mins_peak = [224, 350, 107]       # Minimum taxi time during peak
maxs_peak = [441, 673, 161]       # Maximum taxi time during peak
mins_offpeak = [190, 307, 80]     # Minimum taxi time during off-peak

# === PLOT PEAK PERIOD AS ERRORBARS ===

plt.errorbar(
    x_pos,
    means,
    yerr=[
        [m - mi for m, mi in zip(means, mins_peak)],       # Lower error
        [ma - m for ma, m in zip(maxs_peak, means)]        # Upper error
    ],
    fmt='o',
    capsize=5,
    label='Peak period'
)

# === PLOT OFF-PEAK MINIMUMS AS DIAMONDS ===

plt.scatter(
    x_pos,
    mins_offpeak,
    color='#3e5c76',
    marker='D',
    label='Min Off-peak'
)

# === AXIS AND STYLE CONFIGURATION ===

plt.xticks(x_pos, groups)
plt.xlim(0.8, 3.4)

ax = plt.gca()
ax.set_axisbelow(True)
ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.ylabel('Taxi time (s)', fontsize=12)
plt.xlabel('Hotspot', fontsize=12)
plt.legend()
plt.tight_layout()
plt.show()

