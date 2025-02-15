import pandas as pd
from datetime import datetime, timedelta
import json
from prophet import Prophet
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

# Ejemplo de carga de datos
with open(filename, 'r') as file:
    historical_data = json.load(file)

historical_data = historical_data[data_key]

# Extraer datos en lista
rows = []
for date, buses in historical_data.items():
    for bus_id, stops in buses.items():
        for stop_data in stops:
            rows.append({
                "date": datetime.strptime(date, "%d/%m"),
                "bus_id": bus_id,
                "parada": stop_data["parada"],
                "hora": stop_data["hora"],
                "ocupacion": stop_data["ocupacio"]
            })

df = pd.DataFrame(rows)

# Obtener hora de salida de cada bus (primera parada)
bus_departure = {}
bus_stop_offsets = {}
for bus_id, stops in historical_data["01/01"].items():
    departure_time = datetime.strptime(stops[0]["hora"], "%H:%M:%S").time()
    bus_departure[bus_id] = departure_time
    offsets = {}
    for stop in stops:
        stop_time = datetime.strptime(stop["hora"], "%H:%M:%S").time()
        delta = (stop_time.hour - departure_time.hour) * 60 + (stop_time.minute - departure_time.minute)
        offsets[stop["parada"]] = delta
    bus_stop_offsets[bus_id] = offsets

models = {}

# Entrenar un modelo por (bus, parada)
for (bus_id, parada), group in df.groupby(["bus_id", "parada"]):
# Preparar datos para Prophet
    train_data = group[["date", "ocupacion"]].rename(columns={"date": "ds", "ocupacion": "y"})

    # Modelo y entrenamiento
    model = Prophet(weekly_seasonality=True, daily_seasonality=True)
    model.fit(train_data)

    models[(bus_id, parada)] = model

def predict_week(start_date_str):
    start_date = datetime.strptime(start_date_str, "%d/%m")
    predictions = {}
    
    for day in range(7):
        current_date = start_date + timedelta(days=day)
        date_str = current_date.strftime("%d/%m")
        predictions[date_str] = {}
        
        for bus_id in df["bus_id"].unique():
            predictions[date_str][bus_id] = []
            departure_time = bus_departure[bus_id]
            
            for parada in df[df["bus_id"] == bus_id]["parada"].unique():
                # Obtener modelo y predecir
                model = models.get((bus_id, parada))
                if not model:
                    continue
                
                future = pd.DataFrame({"ds": [current_date]})
                forecast = model.predict(future)
                ocupacion_pred = round(forecast["yhat"].iloc[0])
                
                # Calcular hora de la parada
                offset = bus_stop_offsets[bus_id][parada]
                hora_parada = (
                    datetime.combine(current_date, departure_time) + 
                    timedelta(minutes=offset)
                ).strftime("%H:%M:%S")
                
                predictions[date_str][bus_id].append({
                    "parada": parada,
                    "hora": hora_parada,
                    "ocupacio": max(0, min(100, ocupacion_pred))  # Asegurar rango [0, 100]
                })
    
    return predictions


if __name__ == "__main__":
    start_date = "02/01"
    predicciones = predict_week(start_date)
    predictions_file = f"linia{line_number}_prediccions.json"
    with open(predictions_file, "w") as f:
        json.dump(predicciones, f, indent=2, ensure_ascii=False)