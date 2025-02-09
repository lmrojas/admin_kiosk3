from flask import Flask
from flask_migrate import Migrate
from Admin_Kiosk3_Backend import create_app, db
import os
from dotenv import load_dotenv
import importlib

# Cargar variables de entorno
load_dotenv()

# Lista de servicios (fácil de extender)
SERVICES = [
    'auth_service',
    'kiosk_service',
    'payment_service',
    'ai_service',
    'websocket_service',
    'notification_service'
]

app = create_app()

# Configurar la URL de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurar migraciones para cada servicio
migrations = {}
for service in SERVICES:
    # Importar dinámicamente los modelos de cada servicio
    models = importlib.import_module(f'Admin_Kiosk3_Backend.{service}.models')
    
    # Configurar migración para el servicio
    migrations[service] = Migrate()
    migrations[service].init_app(
        app, 
        db,
        directory=f'migrations/{service}',
        compare_type=True
    )

if __name__ == '__main__':
    app.run()