# Imagen base con Python y bibliotecas de ML
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt /app/requirements.txt



# Instalar dependencias
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar archivos del proyecto
COPY . /app

# Comando por defecto
CMD ["python", "main.py"]