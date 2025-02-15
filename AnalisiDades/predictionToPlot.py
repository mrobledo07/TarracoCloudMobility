import json
import matplotlib.pyplot as plt
from datetime import datetime
import math
import sys

# Validar parámetros: se esperan el nombre del fichero y el día (ej. "02/01")
if len(sys.argv) != 3:
    print("Uso: python script.py <archivo_json> <día>")
    print('Ejemplo: python script.py predicciones.json "02/01"')
    sys.exit(1)

filename = sys.argv[1]
selected_day = sys.argv[2]

# Cargar datos desde el fichero JSON
with open(filename, "r", encoding="utf-8") as f:
    data = json.load(f)

# Verificar que el día seleccionado existe en los datos
if selected_day not in data:
    print(f"No se encontraron datos para el día {selected_day}")
    sys.exit(1)

day_data = data[selected_day]

# Recolectar todas las paradas únicas presentes en el día
all_stops = set()
for bus_id, schedule in day_data.items():
    for entry in schedule:
        stop_name = entry.get("parada", "").strip()
        if stop_name:
            all_stops.add(stop_name)
all_stops = sorted(all_stops)

# Determinar el tamaño de la cuadrícula para los subplots (forma aproximadamente cuadrada)
num_stops = len(all_stops)
num_cols = math.ceil(math.sqrt(num_stops))
num_rows = math.ceil(num_stops / num_cols)

fig, axes = plt.subplots(num_rows, num_cols, figsize=(num_cols * 5, num_rows * 4), squeeze=False)
axes = axes.flatten()

# Para cada parada, graficar la ocupación según la hora para cada autobús
for i, stop in enumerate(all_stops):
    ax = axes[i]
    for bus_id, schedule in day_data.items():
        times = []
        occupancies = []
        for entry in schedule:
            # Comparar nombres de paradas sin distinguir mayúsculas/minúsculas
            if entry.get("parada", "").lower() == stop.lower():
                time_str = entry.get("hora", "").strip()
                if not time_str:
                    continue
                try:
                    # Determinar el formato de la hora según la cantidad de ':'
                    if time_str.count(':') == 2:
                        dt = datetime.strptime(time_str, "%H:%M:%S")
                    else:
                        dt = datetime.strptime(time_str, "%H:%M")
                    # Convertir la hora a un valor decimal (horas)
                    time_val = dt.hour + dt.minute / 60.0 + dt.second / 3600.0
                    times.append(time_val)
                    occupancies.append(entry.get("ocupacio", 0))
                except Exception as e:
                    print(f"Error al parsear la hora '{time_str}' para {bus_id} en la parada {stop}: {e}")
                    continue
        if times:
            # Ordenar los datos por hora
            sorted_pairs = sorted(zip(times, occupancies), key=lambda x: x[0])
            times_sorted, occupancies_sorted = zip(*sorted_pairs)
            ax.plot(times_sorted, occupancies_sorted, marker="o", label=bus_id)
    ax.set_title(stop)
    ax.set_xlabel("Hora del día (horas)")
    ax.set_ylabel("Ocupación (%)")
    ax.grid(True)
    #ax.legend(fontsize="small", loc="best")

# Eliminar subplots vacíos, en caso de que no se utilicen todos
for j in range(i + 1, len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout()
plt.show()
