# Imagen base con Python y bibliotecas de ML
FROM python:3.9-slim

# Copiar archivos del proyecto
WORKDIR /app
COPY . /app

# Instalar dependencias
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Expose API port
EXPOSE 8000

# Comando por defecto
#CMD ["python", "main.py"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]