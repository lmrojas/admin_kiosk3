# Archivo vacío para marcar el directorio como paquete Python 

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from Admin_Kiosk3_Backend.common.config import Config
from Admin_Kiosk3_Backend.common.logging.logger import get_logger

log = get_logger('auth_service')

db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_class=None):
    app = Flask(__name__)
    if config_class is None:
        from .config import Config
        config_class = Config
    
    app.config.from_object(config_class)
    db.init_app(app)
    jwt.init_app(app)
    
    from .routes import auth_bp
    app.register_blueprint(auth_bp)
    
    return app 