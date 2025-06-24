from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np

app = FastAPI()

# Load the pre-trained model
model = joblib.load("model.joblib")

# Definiendo un modelo de datos
class Item(BaseModel):
    Age: int
    Gender: str
    Polyur1a: bool
    Polydipsia: bool
    suddn_weight_loss: bool
    wea_kness: bool
    Polyphagia: bool
    Genital_thrush: bool
    visual_blurring: bool
    Itching: bool
    Irritability: bool
    delayed_healing: bool
    partial_paresis: bool
    muscle_stiffness: bool
    Alopecia: bool
    Obesity: bool

@app.post("/predict")
def predict_item(item: Item):

    features = np.array([list(item.dict().values())])
    
    prediction = model.predict(features)
    category = prediction[0]

    return {"predicted_category": category}
