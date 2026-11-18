# Imagen de la API.
FROM python:3.12-slim

# Sin archivos .pyc y con los logs de Flask apareciendo al instante.
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app

# Las dependencias primero: mientras requirements.txt no cambie, Docker reusa esta capa.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# El código al final: si cambia, solo se rehace desde acá.
COPY app.py .
COPY cine_paradiso_api ./cine_paradiso_api

EXPOSE 5000

# 0.0.0.0 para que se pueda entrar desde afuera del contenedor.
CMD ["flask", "--app", "app", "run", "--host=0.0.0.0", "--port=5000"]
