import os
from Admin_Kiosk3_Backend.common.config import Config as BaseConfig

class Config(BaseConfig):
    """Configuración específica del servicio de pagos"""
    SERVICE_NAME = 'payment_service'
    SERVICE_PORT = 5003
    
    # Configuraciones específicas de pagos
    PAYMENT_TIMEOUT = int(os.environ.get('PAYMENT_TIMEOUT', 300))  # 5 minutos
    MAX_PAYMENT_AMOUNT = float(os.environ.get('MAX_PAYMENT_AMOUNT', 10000.00))

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