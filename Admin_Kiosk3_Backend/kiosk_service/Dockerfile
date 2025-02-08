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
ENV DATABASE_URL=postgresql://admin_kiosk3_user:secure_password@postgres:5432/admin_kiosk3

# Puerto
EXPOSE 5002

# Comando para ejecutar la aplicación
CMD ["flask", "run", "--host=0.0.0.0", "--port=5002"] 