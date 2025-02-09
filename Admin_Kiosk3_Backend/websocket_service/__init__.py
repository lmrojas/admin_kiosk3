# Archivo vacío para marcar el directorio como paquete Python 

from flask import Flask
from flask_socketio import SocketIO
from Admin_Kiosk3_Backend.common.config import Config
from Admin_Kiosk3_Backend.common.logging.logger import get_logger

log = get_logger('websocket_service')
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    Config.init_app(app)
    
    from .models import db
    db.init_app(app)
    socketio.init_app(app)
    
    from .routes import ws_bp
    app.register_blueprint(ws_bp, url_prefix='/ws')
    
    return app 