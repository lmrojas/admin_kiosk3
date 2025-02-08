import os
from Admin_Kiosk3_Backend.common.config import Config as BaseConfig

class Config(BaseConfig):
    """Configuración específica del servicio de kioskos"""
    SERVICE_NAME = 'kiosk_service'
    SERVICE_PORT = 5002
    
    # Configuración de la base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://admin_kiosk3_user:secure_password@localhost:5432/admin_kiosk3'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 30,
        'pool_recycle': 1800,
    }
    
    # Configuraciones específicas de kioskos
    KIOSK_QR_EXPIRY = int(os.environ.get('KIOSK_QR_EXPIRY', 3600))
    KIOSK_ASSIGNMENT_TIMEOUT = int(os.environ.get('KIOSK_ASSIGNMENT_TIMEOUT', 86400))

class DevelopmentConfig(Config):
    """Configuración de desarrollo"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Configuración de producción"""
    DEBUG = False
    SQLALCHEMY_ECHO = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 