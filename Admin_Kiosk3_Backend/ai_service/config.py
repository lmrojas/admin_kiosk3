import os
from Admin_Kiosk3_Backend.common.config import Config as BaseConfig

class Config(BaseConfig):
    """Configuración específica del servicio de IA"""
    SERVICE_NAME = 'ai_service'
    SERVICE_PORT = 5004
    
    # Configuraciones específicas de IA
    MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'model.pkl')
    MODEL_UPDATE_INTERVAL = int(os.environ.get('MODEL_UPDATE_INTERVAL', 86400))  # 24 horas
    PREDICTION_TIMEOUT = int(os.environ.get('PREDICTION_TIMEOUT', 30))  # 30 segundos

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