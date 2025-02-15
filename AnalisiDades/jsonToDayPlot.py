import json
import matplotlib.pyplot as plt
from datetime import datetime
import math
import sys  

# Validar parámetro
if len(sys.argv) != 2:
    print("Uso: python script.py <número_línea>")
    print("Ejemplo: python script.py 54")
    exit(1)

line_number = sys.argv[1]
if line_number not in ("41", "54"):
    print("Número de línea inválido. Usar 41 o 54")
    exit(1)

# Cargar datos según parámetro (modificado)
filename = f"linia{line_number}_any_complet.json"  # Nombre dinámico del archivo
data_key = f"linia_{line_number}"  # Clave dinámica en el JSON

with open(filename, "r", encoding="utf-8") as f:
    data = json.load(f)

# Seleccionar día (resto del código igual)
selected_day = "01/01"
day_data = data.get(data_key, {}).get(selected_day)  # Clave dinámica aquí
if not day_data:
    print(f"No data found for day {selected_day}")
    exit()

# ... (el resto del código permanece igual)

# Gather all unique stops for the day
all_stops = set()
for bus_id, schedule in day_data.items():
    for entry in schedule:
        stop_name = entry.get("parada", "").strip()
        if stop_name:
            all_stops.add(stop_name)
all_stops = sorted(all_stops)

# Determine grid size for subplots (roughly square)
num_stops = len(all_stops)
num_cols = math.ceil(math.sqrt(num_stops))
num_rows = math.ceil(num_stops / num_cols)

fig, axes = plt.subplots(num_rows, num_cols, figsize=(num_cols * 5, num_rows * 4), squeeze=False)
axes = axes.flatten()

# Create a plot for each stop
for i, stop in enumerate(all_stops):
    ax = axes[i]
    for bus_id, schedule in day_data.items():
        times = []
        occupancies = []
        for entry in schedule:
            # Compare stop names case-insensitively
            if entry.get("parada", "").lower() == stop.lower():
                time_str = entry.get("hora", "").strip()
                if not time_str:
                    continue
                try:
                    # Use the proper format depending on whether seconds are present
                    if time_str.count(':') == 2:
                        dt = datetime.strptime(time_str, "%H:%M:%S")
                    else:
                        dt = datetime.strptime(time_str, "%H:%M")
                    # Convert time to decimal hours (including seconds)
                    time_val = dt.hour + dt.minute / 60.0 + dt.second / 3600.0
                    times.append(time_val)
                    occupancies.append(entry.get("ocupacio", 0))
                except Exception as e:
                    print(f"Error parsing time '{time_str}' for {bus_id} at stop {stop}: {e}")
                    continue
        if times:
            # Sort times and occupancies together
            sorted_pairs = sorted(zip(times, occupancies), key=lambda x: x[0])
            times_sorted, occupancies_sorted = zip(*sorted_pairs)
            ax.plot(times_sorted, occupancies_sorted, marker="o", label=bus_id)
    ax.set_title(stop)
    ax.set_xlabel("Time of Day (hours)")
    ax.set_ylabel("Occupancy (%)")
    #ax.legend(fontsize="small", loc="best")
    ax.grid(True)

# Remove any unused subplots
for j in range(i + 1, len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout()
plt.show()