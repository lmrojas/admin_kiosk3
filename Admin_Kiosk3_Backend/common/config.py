import os

class Config:
    """Configuración base compartida"""
    # Configuración de base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://user:password@db:5432/admin_kiosk3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'super-secret-key')
    
    # Configuración de Redis (para cache/websockets)
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/0')

def init_app(app):
    """Inicializar configuración en la app Flask"""
    app.config.from_object(Config)

def get_config():
    """Obtener configuración según entorno"""
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        return ProductionConfig()
    return DevelopmentConfig()

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False 