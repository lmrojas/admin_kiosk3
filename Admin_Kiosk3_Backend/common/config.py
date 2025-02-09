import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración base compartida"""
    # Configuración de base de datos
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://admin_kiosk3_user:secure_password@localhost:5432/admin_kiosk3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'super-secret-key')
    
    # Configuración de Redis (para cache/websockets)
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/0')

    @staticmethod
    def validate_database_config(app):
        """Validar configuración de base de datos según reglas MDC"""
        required_configs = [
            'SQLALCHEMY_DATABASE_URI',
            'SQLALCHEMY_TRACK_MODIFICATIONS'
        ]
        
        for config in required_configs:
            if config not in app.config:
                raise ValueError(f"Falta configuración requerida: {config}")
                
        # Validar formato de DATABASE_URL
        db_url = app.config['SQLALCHEMY_DATABASE_URI']
        if not db_url.startswith('postgresql://'):
            raise ValueError("DATABASE_URL debe ser PostgreSQL")
            
        # Validar esquemas requeridos
        required_schemas = ['auth', 'kiosk', 'payment', 'notify', 'ws', 'ai']
        for schema in required_schemas:
            if schema not in db_url:
                app.logger.warning(f"Esquema {schema} no encontrado en DATABASE_URL")
                
        return True

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