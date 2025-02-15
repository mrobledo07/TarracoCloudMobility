import json
import matplotlib.pyplot as plt
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

line_data = data.get(data_key, {})

# Estructura para almacenar los valores de ocupación por estación y por mes
# monthly_data: { station: { month (int): [ocupacion1, ocupacion2, ...] } }
monthly_data = {}

# Iteramos sobre cada día del año (la clave tiene formato "DD/MM")
for date_str, buses in line_data.items():
    try:
        # Extraer el día y el mes a partir de la cadena "DD/MM"
        day_str, month_str = date_str.split("/")
        month_int = int(month_str)
    except Exception as e:
        print(f"Error procesando la fecha '{date_str}': {e}")
        continue

    # Iterar por cada bus en ese día
    for bus_id, stops in buses.items():
        # Para cada parada del bus
        for entry in stops:
            station = entry.get("parada", "").strip()
            occ = entry.get("ocupacio", None)
            if station and occ is not None:
                if station not in monthly_data:
                    monthly_data[station] = {}
                if month_int not in monthly_data[station]:
                    monthly_data[station][month_int] = []
                monthly_data[station][month_int].append(occ)

# Calcular la ocupación media mensual para cada estación
# monthly_averages: { station: { month (1-12): average_occupancy or None } }
monthly_averages = {}
for station, month_dict in monthly_data.items():
    monthly_averages[station] = {}
    for month in range(1, 13):
        values = month_dict.get(month, [])
        if values:
            avg = sum(values) / len(values)
        else:
            avg = None  # No hay datos para ese mes
        monthly_averages[station][month] = avg

# Preparar la visualización: una gráfica anual (meses) para cada estación.
stations = sorted(monthly_averages.keys())
num_stations = len(stations)
num_cols = math.ceil(math.sqrt(num_stations))
num_rows = math.ceil(num_stations / num_cols)

fig, axes = plt.subplots(num_rows, num_cols, figsize=(num_cols * 5, num_rows * 4), squeeze=False)
axes = axes.flatten()

months = list(range(1, 13))
month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

for i, station in enumerate(stations):
    ax = axes[i]
    avg_values = [monthly_averages[station][m] for m in months]
    ax.plot(months, avg_values, marker="o", linestyle="-")
    ax.set_title(station)
    ax.set_xticks(months)
    ax.set_xticklabels(month_labels)
    ax.set_xlabel("Month")
    ax.set_ylabel("Average Occupancy (%)")
    ax.grid(True)

# Eliminar subplots vacíos si los hubiera
for j in range(i + 1, len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout()
plt.show()


"""
En el script, la media de ocupación para cada estación y cada mes se calcula siguiendo estos pasos:

1. **Recopilación de datos:**  
   Se recorre el JSON generado y para cada día se extrae el mes a partir de la fecha (por ejemplo, "01/01" se descompone en día y mes).  
   Luego, para cada bus y para cada parada (estación) se guarda el valor de ocupación (el campo `"ocupacio"`) en una estructura de datos que agrupa esos valores por estación y por mes.

2. **Cálculo de la media:**  
   Una vez que se tienen todas las ocupaciones para una determinada estación en un mes, se suma todos esos valores y se divide entre la cantidad de registros para ese mes.
   Esto se realiza para cada mes (de 1 a 12) y para cada estación.

Este proceso se repite para cada estación y para cada mes, de modo que finalmente se obtiene una serie de 12 valores (uno por mes) que representan la evolución de la ocupación media en esa estación a lo largo del año.

"""
