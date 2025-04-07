import matplotlib.pyplot as plt
import numpy as np

# # Dades
# hours = ['7-8', '8-9', '9-10', '10-11', '11-12', '12-13', '13-14', '14-15',
#          '15-16', '16-17', '17-18', '18-19', '19-20', '20-21', '21-22']
# L2 = [44, 45, 54, 36, 43, 55, 81, 53, 36, 36, 21, 24, 34, 43, 25]
# L3 = [10, 10, 9, 8, 10, 19, 10, 14, 21, 16, 6, 8, 12, 11, 4]
# L4 = [4, 6, 3, 6, 1, 5, 4, 6, 8, 4, 3, 2, 2, 3, 1]
# L5 = [1, 1, 2, 0, 0, 1, 2, 2, 2, 1, 0, 1, 1, 4, 0]

# x = np.arange(len(hours))

# colors = {
#     "L2": "#2c3e50",  # azul gris oscuro (nivel base)
#     "L3": "#3e5c76",  # azul intermedio
#     "L4": "#5388b3",  # azul más claro, más saturado
#     "L5": "#7fbfff"   # azul cielo claro
# }

# fig, ax = plt.subplots(figsize=(14, 6))

# bar2 = ax.bar(x, L2, label='Level 2', color=colors["L2"])
# bar3 = ax.bar(x, L3, bottom=L2, label='Level 3', color=colors["L3"])
# bar4 = ax.bar(x, L4, bottom=np.array(L2)+np.array(L3), label='Level 4', color=colors["L4"])
# bar5 = ax.bar(x, L5, bottom=np.array(L2)+np.array(L3)+np.array(L4), label='Level 5', color=colors["L5"])

# # Etiquetes just a l’inici de cada barra apilada
# for i in range(len(x)):
#     ax.text(x[i], 0, str(L2[i]), ha='center', va='bottom', fontsize=10, weight='bold')
#     ax.text(x[i], L2[i], str(L3[i]), ha='center', va='bottom', fontsize=10, weight='bold')
#     ax.text(x[i], L2[i] + L3[i], str(L4[i]), ha='center', va='bottom', fontsize=10, weight='bold')
#     if L5[i] > 0:
#         ax.text(x[i], L2[i] + L3[i] + L4[i], str(L5[i]), ha='center', va='bottom', fontsize=10, weight='bold')

# # Format eixos i títols
# ax.set_xticks(x)
# ax.set_xticklabels(hours, rotation=45, fontsize=12)
# ax.set_ylabel("Number of Hotspots", fontsize=12)
# # ax.set_title("Hotspots per Hour by Level (Levels 2–5)")
# ax.legend(fontsize=12)
# plt.yticks(fontsize=12)
# # ax.grid(axis='y', linestyle='--', alpha=0.5)
# plt.tight_layout()
# plt.show()


### METHOD 2 ###

# Datos del método 1
hours = ['7-8', '8-9', '9-10', '10-11', '11-12', '12-13', '13-14', '14-15',
         '15-16', '16-17', '17-18', '18-19', '19-20', '20-21', '21-22']
values = [10, 6, 8, 3, 7, 10, 16, 13, 10, 7, 2, 4, 6, 8, 3]

# Crear figura
plt.figure(figsize=(12, 6))

# Dibujar línea con puntos
plt.plot(hours, values, color='#34495e', marker='o', linewidth=2, label='Hotspots')

# Rellenar el área debajo de la línea
plt.fill_between(hours, values, color='#34495e', alpha=0.3)

# Etiquetas de los puntos
for i, val in enumerate(values):
    plt.text(i, val + 0.5, str(val), ha='center', va='bottom', fontsize=10, fontweight='bold')

# Títulos y estilo
plt.xticks(hours, rotation=45, fontsize=12)
plt.ylim(0, max(values) + 3)  # Ajusta el límite superior
plt.yticks(range(0, max(values) + 4, 2), fontsize=12)  # Ticks de 2 en 2
plt.ylabel("Number of Hotspots", fontsize=12)
plt.grid(alpha=0.3)
plt.tight_layout()

plt.show()


