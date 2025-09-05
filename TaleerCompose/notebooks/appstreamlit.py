import streamlit as st
import requests

st.title("Predicción de Diabetes")

# Definir los campos del formulario
age = st.number_input("Edad", min_value=16, max_value=90, value=40)
gender = st.selectbox("Género", options=[("Masculino", 1), ("Femenino", 0)], format_func=lambda x: x[0])[1]
polyuria = st.selectbox("Polyur1a", [0, 1])
polydipsia = st.selectbox("Polydipsia", [0, 1])
suddn_weight_loss = st.selectbox("Suddn weight loss", [0, 1])
wea_kness = st.selectbox("Wea kness", [0, 1])
polyphagia = st.selectbox("Polyphagia", [0, 1])
genital_thrush = st.selectbox("Genital thrush", [0, 1])
visual_blurring = st.selectbox("Visual blurring", [0, 1])
itching = st.selectbox("Itching", [0, 1])
irritability = st.selectbox("Irritability", [0, 1])
delayed_healing = st.selectbox("Delayed healing", [0, 1])
partial_paresis = st.selectbox("Partial paresis", [0, 1])
muscle_stiffness = st.selectbox("Muscle stiffness", [0, 1])
alopecia = st.selectbox("Alopecia", [0, 1])
obesity = st.selectbox("Obesity", [0, 1])

if st.button("Predecir"):
    data = {
        "Age": age,
        "Gender": gender,
        "Polyur1a": polyuria,
        "Polydipsia": polydipsia,
        "suddn_weight_loss": suddn_weight_loss,
        "wea_kness": wea_kness,
        "Polyphagia": polyphagia,
        "Genital_thrush": genital_thrush,
        "visual_blurring": visual_blurring,
        "Itching": itching,
        "Irritability": irritability,
        "delayed_healing": delayed_healing,
        "partial_paresis": partial_paresis,
        "muscle_stiffness": muscle_stiffness,
        "Alopecia": alopecia,
        "Obesity": obesity
    }
    try:
        response = requests.post("http://localhost:8000/predict", json=data)
        if response.status_code == 200:
            result = response.json()
            st.success(f"Categoría predicha: {result['predicted_category']}")
        else:
            st.error(f"Error: {response.json()['detail']}")
    except Exception as e:
        st.error(f"Error de conexión: {e}")