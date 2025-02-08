import os
from Admin_Kiosk3_Backend.common.config import Config as BaseConfig

class Config(BaseConfig):
    """Configuración específica del servicio de notificaciones"""
    SERVICE_NAME = 'notification_service'
    SERVICE_PORT = 5006
    
    # Configuraciones específicas de notificaciones
    EMAIL_RETRY_ATTEMPTS = int(os.environ.get('EMAIL_RETRY_ATTEMPTS', 3))
    EMAIL_RETRY_DELAY = int(os.environ.get('EMAIL_RETRY_DELAY', 300))  # 5 minutos
    SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))

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