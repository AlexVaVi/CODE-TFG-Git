import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline

# result = pd.read_csv("runway_hourly_stats.csv")

# # Agrupación como antes
# grouped = result.groupby(['used_runway', 'total_operations']).agg(
#     avg_runway_time=('median_runway_time', 'mean')
# ).reset_index()

# # Paleta azul-gris personalizada
# colors = {
#     '1': '#7fbfff',  # azul clarito
#     '2': '#3e5c76',  # azul medio
#     '3': '#bdbdbd',  # azul oscuro
#     # añade más pistas si tienes más
# }

# plt.figure(figsize=(14, 6))  # Más ancho

# for runway, df_rwy in grouped.groupby('used_runway'):
#     x = df_rwy['avg_runway_time'].dropna()

#     if len(x) > 1:
#         kde = gaussian_kde(x)
#         x_range = np.linspace(x.min(), x.max(), 200)
#         y = kde(x_range)
        
#         color = colors.get(str(runway), '#666666')  # default gris oscuro si no definido
#         plt.plot(x_range, y, label=f'Runway {runway}', linewidth=2, color=color)
#         plt.fill_between(x_range, y, alpha=0.3, color=color)

# === 1. Cargar los 4 CSV ===

files = [
    r"C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\October\RunwayUsage\runway_hourly_stats22.csv",
    r"C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\October\RunwayUsage\runway_hourly_stats23.csv",
    r"C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\October\RunwayUsage\runway_hourly_stats24.csv",
    r"C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\October\RunwayUsage\runway_hourly_stats25.csv",
    r"C:\Users\alexv\OneDrive\Escritorio\UPC\TFG\DATA\October\RunwayUsage\runway_hourly_stats26.csv",
]


df_list = [pd.read_csv(f) for f in files]
df_all = pd.concat(df_list, ignore_index=True)

# Eliminar runway times negativos o nulos
df_all = df_all[df_all['median_runway_time'] > 10]
df_all = df_all[df_all['median_runway_time'] < 160]

# === 2. Normalizar tipos ===
df_all['used_runway'] = df_all['used_runway'].astype(str).str.strip()

# === 4. Preparar gráfica de eficiencia ===
colors = {
    '1': '#7fbfff',
    '2': '#3e5c76',
    '3': '#bdbdbd',
}

plt.figure(figsize=(14, 6))

for runway, df_rwy in df_all.groupby('used_runway'):
    # Agrupar por total_operations para promediar si hay varias entradas
    df_rwy = df_rwy[df_rwy['median_runway_time'].between(10, 160)]
    
    df_rwy_grouped = df_rwy.groupby('total_operations').agg(
        avg_runway_time=('median_runway_time', 'mean')
    ).reset_index()
    
    x = df_rwy_grouped['total_operations']
    y = df_rwy_grouped['avg_runway_time']

    if len(x) >= 4:
        spline = make_interp_spline(x, y, k=1)
        x_smooth = np.linspace(x.min(), x.max(), 300)
        y_smooth = spline(x_smooth)

        color = colors.get(runway, '#666666')
        plt.plot(x_smooth, y_smooth, label=f'Runway {runway}', linewidth=3, color=color)
    else:
        plt.plot(x, y, label=f'Runway {runway}', linewidth=3, color=color, marker='o')
        

# Estética
ax = plt.gca()
ax.set_axisbelow(True)
ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.xlabel('Number of operations per hour', fontsize=12)
plt.ylabel('Average runway time (seconds)', fontsize=12)
plt.ylim(0, 140)
plt.yticks(range(0, 121, 10))
plt.xlim(left=0)
plt.legend(fontsize=10)
plt.tight_layout()
plt.show()
