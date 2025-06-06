import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# DATA FOR AIRLINE COSTS AT HOTSPOTS
data = {
    "H1": {
        "SAS": [406, 8861.9, 460818.8],
        "NSZ": [140, 3056.7, 158948.1],
        "RYR": [72, 1571.5, 81717.8],
        "DLH": [32, 698.5, 36321.5],
        "FIN": [34, 741.9, 38578.7],
        "NOZ": [28, 611.9, 31821.1],
        "QTR": [2, 43.7, 2270.4],
        "UAE": [4, 87.4, 4539.5]
    },
    "H2": {
        "SAS": [188, 8375.1, 435505.8],
        "NSZ": [59, 2627.3, 136620.2],
        "RYR": [25, 1113.2, 57887.4],
        "DLH": [18, 800.3, 41613.7],
        "FIN": [15, 666.7, 34666.7],
        "NOZ": [13, 578.0, 30056.2],
        "UAE": [3, 133.6, 6948.8],
        "ETH": [3, 133.6, 6948.8],
        "QTR": [1, 44.5, 2312.7]
    },
    "H3": {
        "SAS": [316, 8977.8, 466842.9],
        "NSZ": [102, 2899.3, 150364.6],
        "RYR": [68, 1933.0, 100516.2],
        "DLH": [26, 739.0, 38428.9],
        "FIN": [23, 653.1, 33959.4],
        "NOZ": [25, 709.8, 36863.3],
        "UAE": [2, 56.8, 2953.6],
        "ETH": [4, 113.6, 5907.1]
    }
}

fig, axes = plt.subplots(1, 3, figsize=(18, 8))
colors = ["#CEE3F6", "#A9D0F5", "#81BEF7"]
highlight = "#2E64FE"
annual_alpha = 0.4

for ax, (hotspot, airlines) in zip(axes, data.items()):
    df = pd.DataFrame(airlines, index=["Flights", "Weekly Cost (€)", "Annual Cost (€)"]).T
    ax.axis('off')
    ax.set_title(f"{hotspot}", fontsize=16, weight='bold')
    
    # Draw table
    col_labels = ["Airline", "Flights", "Weekly (€)", "Annual (€)"]
    row_height = 1.2
    width = [0.5, 0.5, 0.7, 1.0]
    
    # Header
    for i, label in enumerate(col_labels):
        ax.text(sum(width[:i]) + 0.05, row_height * len(df) + 0.2, label, fontsize=12, weight='bold', color="white", bbox=dict(facecolor=highlight, edgecolor='none', boxstyle='round,pad=0.2'))
    
    # Rows
    for idx, (airline, row) in enumerate(df.iterrows()):
        y = row_height * (len(df) - idx - 1)
        ax.text(width[0]/2, y, airline, fontsize=11, ha='center', va='center')
        ax.text(sum(width[:1]) + 0.05, y, int(row["Flights"]), fontsize=11)
        ax.text(sum(width[:2]) + 0.05, y, f"{row['Weekly Cost (€)']:.0f}", fontsize=11)
        ax.text(sum(width[:3]) + 0.05, y, f"{row['Annual Cost (€)']:.0f}", fontsize=11, alpha=annual_alpha)

plt.tight_layout()
plt.subplots_adjust(wspace=0.4)
plt.show()
