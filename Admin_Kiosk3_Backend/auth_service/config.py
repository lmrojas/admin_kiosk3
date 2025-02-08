import os
from Admin_Kiosk3_Backend.common.config import Config as BaseConfig

class Config(BaseConfig):
    """Configuración específica del servicio de autenticación"""
    SERVICE_NAME = 'auth_service'
    SERVICE_PORT = 5001
    
    # Configuración JWT específica
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))  # 1 hora
    JWT_REFRESH_TOKEN_EXPIRES = int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 2592000))  # 30 días

class DevelopmentConfig(Config):
    """Configuración de desarrollo"""
    DEBUG = True

class ProductionConfig(Config):
    """Configuración de producción"""
    DEBUG = False

# Configuración por defecto
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 