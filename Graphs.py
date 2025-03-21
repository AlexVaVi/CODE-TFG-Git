import matplotlib.pyplot as plt
import numpy as np

# Ejemplo de datos (sustitúyelos con los tuyos)
days = ['Oct 20', 'Oct 21', 'Oct 22', 'Oct 23', 'Oct 24', 'Oct 25', 'Oct 26', 'Oct 27']
opensky = [488, 573, 576, 599, 589, 601, 430, 487]  # <-- tus valores post-processed
flightradar = [590, 618, 623, 632, 632, 623, 440, 539]  # <-- valores reales de comparación

x = np.arange(len(days))
width = 0.3

# Crear figura
fig, ax = plt.subplots(figsize=(12,6))

# Colores más suaves y estilos
rects1 = ax.bar(x - width/2, opensky, width, label='OpenSky (Post-Processed)', 
                color='#444444', edgecolor='none')
rects2 = ax.bar(x + width/2, flightradar, width, label='FlightRadar24', 
                color='#4C78A8', edgecolor='none')

# Títulos y etiquetas con estilo
ax.set_ylabel('Number of Flights', fontsize=12)
# ax.set_title('Daily Flight Operations Comparison at Arlanda Airport', fontsize=16, pad=20)
ax.set_xticks(x)
ax.set_xticklabels(days, fontsize=12)
ax.tick_params(axis='y', labelsize=12)

# Líneas suaves y fondo limpio
# ax.grid(axis='y', linestyle='--', linewidth=0.6, alpha=0.6)
ax.set_axisbelow(True)
ax.set_facecolor('white')
fig.patch.set_facecolor('white')

# Leyenda elegante
ax.legend(fontsize=12, loc='upper right', frameon=False)

# Etiquetas encima de las barras
for bars in [rects1, rects2]:
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height}',
                    xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 5),  # desplazamiento
                    textcoords='offset points',
                    ha='center', va='bottom',
                    fontsize=10)

plt.tight_layout()
plt.subplots_adjust(top=1.0)
plt.savefig('flight_comparison_clean.png', bbox_inches='tight', dpi=300)
plt.show()
