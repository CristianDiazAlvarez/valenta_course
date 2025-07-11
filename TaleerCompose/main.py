from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd
import os

app = FastAPI()

# Load the pre-trained model
#model = joblib.load("model.pkl")

# Definiendo un modelo de datos
class Item(BaseModel):
    Age: int = 40
    Gender: int = 1
    Polyur1a: bool = 0
    Polydipsia: bool = 1
    suddn_weight_loss: bool = 0
    wea_kness: bool = 1
    Polyphagia: bool = 0
    Genital_thrush: bool = 0
    visual_blurring: bool = 0
    Itching: bool = 1
    Irritability: bool = 0
    delayed_healing: bool = 1
    partial_paresis: bool = 0
    muscle_stiffness: bool = 1
    Alopecia: bool = 1
    Obesity: bool = 1


@app.get("/checkmodels")
def check_models():

    # Ruta del directorio que quieres explorar
    directorio = '/app/notebooks'

    # Listar y filtrar archivos que terminan en .pkl
    archivos_pkl = [f for f in os.listdir(directorio) if f.endswith('.pkl')]

    return archivos_pkl
 

@app.post("/predict")
def predict_item(item: Item):
    try:
        features = item.dict()
        # Convertir a DataFrame de una sola fila
        input_df = pd.DataFrame([features])
        prediction = model.predict(input_df)
        category = int(prediction[0])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"predicted_category": category}
