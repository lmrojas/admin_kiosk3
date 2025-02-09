"""
Common package for shared functionality across services
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    """Inicializar la base de datos con la aplicación"""
    db.init_app(app)

def get_schema_for_service(service_name):
    """Helper para obtener el nombre del esquema para un servicio"""
    schema_map = {
        'auth': 'auth',
        'kiosk': 'kiosk',
        'payment': 'payment',
        'ai': 'ai',
        'ws': 'ws',
        'notify': 'notify'
    }
    return schema_map.get(service_name, 'public')

# Exportar lo que otros módulos necesitarán
__all__ = ['db', 'init_db', 'get_schema_for_service']