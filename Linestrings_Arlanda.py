import pandas as pd
from shapely.geometry import Point, LineString
import matplotlib.pyplot as plt
from conversion import latlon_to_xy

ref_lat = 40.416775
ref_lon = -3.703790

df = pd.read_csv(r'C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\arlanda_airport_nodes.csv', delimiter=',')

x, y = latlon_to_xy(df["latitude"].values, df["longitude"].values, ref_lat, ref_lon)
df["x"] = x
df["y"] = y

linestrings = {}
for (way_type, way_id), group in df.groupby(["type", "way_id"]):
    points = [Point(row["x"], row["y"]) for _, row in group.iterrows()]
    if len(points) >= 2:
        line = LineString(points)
        linestrings[(way_type, way_id)] = line
    
print(linestrings)
print(len(linestrings))

# fig, ax = plt.subplots(figsize=(10, 10))

# labels_plotted = {}

# for (way_type, way_id), line in linestrings.items():
#     x, y = line.xy  
#     if way_type.lower() == 'taxiway':
#         color = 'blue'
#         label = 'Taxiway'
#     elif way_type.lower() == 'runway':
#         color = 'red'
#         label = 'Runway'
#     else:
#         color = 'gray'
#         label = way_type

#     if label not in labels_plotted:
#         ax.plot(x, y, color=color, linewidth=2, label=label)
#         labels_plotted[label] = True
#     else:
#         ax.plot(x, y, color=color, linewidth=2)

# ax.set_xlabel("Longitud")
# ax.set_ylabel("Latitud")
# ax.set_title("Segmentos del aeropuerto")
# ax.legend()

# plt.show()