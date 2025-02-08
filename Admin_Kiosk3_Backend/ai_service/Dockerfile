# Imagen base Python con soporte para ML
FROM python:3.9-slim

# Instalar dependencias del sistema para scikit-learn
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo
WORKDIR /app

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente y modelos
COPY . .

# Variables de entorno
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Puerto
EXPOSE 5004

# Comando para ejecutar la aplicación
CMD ["flask", "run", "--host=0.0.0.0", "--port=5004"] 