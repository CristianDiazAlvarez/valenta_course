from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import random
import requests
import json
import time
import csv
import os

MIN_UPDATE_TIME = 30## 300 ## Aca pueden cambiar el tiempo minimo para cambiar bloque de información

app = FastAPI()

class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: str = "OK"


@app.get("/health",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
def get_health() -> HealthCheck:
    """
    ## Perform a Health Check
    Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
    to ensure a robust container orchestration and management is in place. Other
    services which rely on proper functioning of the API service will not deploy if this
    endpoint returns any other HTTP status code except 200 (OK).
    Returns:
        HealthCheck: Returns a JSON response with the health status
    """
    return HealthCheck(status="OK")

# Elevation,
# Aspect,
# Slope,
# Horizontal_Distance_To_Hydrology,
# Vertical_Distance_To_Hydrology,
# Horizontal_Distance_To_Roadways,
# Hillshade_9am,
# Hillshade_Noon,
# Hillshade_3pm,
# Horizontal_Distance_To_Fire_Points,
# Wilderness_Area,
# Soil_Type,
# Cover_Type

@app.get("/")
async def root():
    return {"Proyecto": "Extracción de datos, entrenamiento de modelos."}


# Cargar los datos del archivo CSV
## download the dataset
# Directory of the raw data files
_data_root = './data/covertype'
# Path to the raw training data
_data_filepath = os.path.join(_data_root, 'covertype_train.csv')
# Download data
os.makedirs(_data_root, exist_ok=True)
if not os.path.isfile(_data_filepath):
    #https://archive.ics.uci.edu/ml/machine-learning-databases/covtype/
    url = 'https://docs.google.com/uc?export=download&confirm={{VALUE}}&id=1lVF1BCWLH4eXXV_YOJzjR7xZjj-wAGj9'
    r = requests.get(url, allow_redirects=True, stream=True)
    open(_data_filepath, 'wb').write(r.content)
    
data = []
with open(_data_filepath, newline='') as csvfile:
    reader = csv.reader(csvfile)
    next(reader, None)
    for row in reader:
        data.append(row)

batch_size = len(data) // 10

# Definir la función para generar la fracción de datos aleatoria
def get_batch_data(batch_number:int, batch_size:int=batch_size):
    start_index = batch_number * batch_size
    end_index = start_index + batch_size
    # Obtener datos aleatorios dentro del rango del grupo
    random_data = random.sample(data[start_index:end_index], batch_size // 10)
    return random_data

# Cargar información previa si existe
if os.path.isfile('/data/timestamps.json'):
    with open('/data/timestamps.json', "r") as f:
        timestamps = json.load(f)
        
else:
    # Definir el diccionario para almacenar los timestamps de cada grupo e incializar el conteo, inicia en -1 para no agregar logica adicional de conteo
    timestamps = {str(group_number): [0, -1] for group_number in range(1, 11)} # el valor está definido como [timestamp, batch]

# Definir la ruta de la API
@app.get("/data")
async def read_data(group_number: int):
    global timestamps

    # Verificar si el número de grupo es válido
    if group_number < 1 or group_number > 10:
        raise HTTPException(status_code=400, detail="Número de grupo inválido")
    # Verificar si el número de conteo es adecuado
    if timestamps[str(group_number)][1] >= 10:
        raise HTTPException(status_code=400, detail="Ya se recolectó toda la información minima necesaria")
    
    current_time = time.time()
    last_update_time = timestamps[str(group_number)][0]
    
    # Verificar si han pasado más de 5 minutos desde la última actualización
    if current_time - last_update_time > MIN_UPDATE_TIME: 
        # Actualizar el timestamp y obtener nuevos datos
        timestamps[str(group_number)][0] = current_time
        timestamps[str(group_number)][1] += 1 #2 if timestamps[str(group_number)][1] == -1 else 1
    
    # Utilizar los mismos datos que la última vez (una parte del mismo grupo de información)
    random_data = get_batch_data(timestamps[str(group_number)][1]) # cambio importante
    with open('/data/timestamps.json', 'w') as file:
        file.write(json.dumps(timestamps))
    
    return {"group_number": group_number, "batch_number": timestamps[str(group_number)][1], "data": random_data}

@app.get("/restart_data_generation")
async def restart_data(group_number: int):
    # Verificar si el número de grupo es válido
    if group_number < 1 or group_number > 10:
        raise HTTPException(status_code=400, detail="Número de grupo inválido")

    timestamps[str(group_number)][0] = 0
    timestamps[str(group_number)][1] = -1
    with open('/data/timestamps.json', 'w') as file:
        file.write(json.dumps(timestamps))
    return {'ok'}