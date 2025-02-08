# Imagen base Python
FROM python:3.9-slim

# Directorio de trabajo
WORKDIR /app

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Variables de entorno
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Puerto para WebSocket
EXPOSE 5005

# Comando para ejecutar la aplicación
CMD ["flask", "run", "--host=0.0.0.0", "--port=5005"] 