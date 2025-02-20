"""Configuración independiente del servicio de autenticación"""
import os
from datetime import timedelta

class Config:
    """Configuración base"""
    
    # Identificación del servicio
    SERVICE_NAME = 'auth_service'
    SERVICE_PORT = int(os.getenv('AUTH_SERVICE_PORT', 5001))
    
    # Base de datos específica para auth
    SQLALCHEMY_DATABASE_URI = 'postgresql://admin_kiosk3_user:secure_password@localhost:5432/admin_kiosk3'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración JWT
    JWT_SECRET_KEY = os.getenv('AUTH_JWT_SECRET_KEY', 'super-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_ERROR_MESSAGE_KEY = 'error'
    
    # Configuración de seguridad
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_SPECIAL = True
    PASSWORD_REQUIRE_NUMBERS = True
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_TIME = timedelta(minutes=15)
    PASSWORD_SALT = os.getenv('PASSWORD_SALT', 'change-me-in-production')
    BCRYPT_LOG_ROUNDS = 12
    
    # Configuración de correo para recuperación de contraseña
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    
    # Roles y permisos por defecto
    DEFAULT_ROLES = {
        'admin': {
            'description': 'Administrador del sistema',
            'permissions': {'all': True}
        },
        'operator': {
            'description': 'Operador de kioscos',
            'permissions': {
                'kiosks': {'read': True, 'write': True},
                'payments': {'read': True},
                'profile': {'read': True, 'write': True}
            }
        },
        'viewer': {
            'description': 'Visualizador',
            'permissions': {
                'kiosks': {'read': True},
                'profile': {'read': True}
            }
        }
    }

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False
    
    # Configuración JWT para desarrollo
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)  # Más tiempo en desarrollo
    
    # Logging más detallado
    LOG_LEVEL = 'DEBUG'

class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    DEBUG = False
    
    # Base de datos de test en PostgreSQL
    SQLALCHEMY_DATABASE_URI = (
        'postgresql://admin_kiosk3_user:secure_password@localhost:5432/admin_kiosk3_test'
    )
    
    # Configuración JWT para testing
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    
    # Deshabilitar CSRF en testing
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False
    
    # Configuraciones de seguridad adicionales
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
    # Logging más restrictivo
    LOG_LEVEL = 'WARNING'

# Mapeo de configuraciones
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 