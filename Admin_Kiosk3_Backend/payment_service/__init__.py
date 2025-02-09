from flask import Flask
from Admin_Kiosk3_Backend.common.config import Config
from Admin_Kiosk3_Backend.common.logging.logger import get_logger

log = get_logger('payment_service')

def create_app():
    app = Flask(__name__)
    Config.init_app(app)
    
    from .models import db
    db.init_app(app)
    
    from .routes import payment_bp
    app.register_blueprint(payment_bp, url_prefix='/payments')
    
    return app