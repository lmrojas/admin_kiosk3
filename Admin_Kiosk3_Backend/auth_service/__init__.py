# Archivo vacío para marcar el directorio como paquete Python 

from flask import Flask
from Admin_Kiosk3_Backend.common.config import Config
from Admin_Kiosk3_Backend.common.logging.logger import get_logger

log = get_logger('auth_service')

def create_app():
    app = Flask(__name__)
    Config.init_app(app)
    
    from .models import db
    db.init_app(app)
    
    from .routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    return app 