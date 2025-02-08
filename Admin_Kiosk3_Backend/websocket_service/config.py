import os
from Admin_Kiosk3_Backend.common.config import Config as BaseConfig

class Config(BaseConfig):
    """Configuración específica del servicio de WebSocket"""
    SERVICE_NAME = 'websocket_service'
    SERVICE_PORT = 5005
    
    # Configuraciones específicas de WebSocket
    SOCKET_PING_TIMEOUT = int(os.environ.get('SOCKET_PING_TIMEOUT', 60))  # 1 minuto
    SOCKET_PING_INTERVAL = int(os.environ.get('SOCKET_PING_INTERVAL', 25))  # 25 segundos

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