from flask import Flask
from celery import Celery
from Admin_Kiosk3_Backend.common.config import Config
from Admin_Kiosk3_Backend.common.logging.logger import get_logger

log = get_logger('notification_service')
celery = Celery('notification_service')

def create_app():
    app = Flask(__name__)
    Config.init_app(app)
    
    from .models import db
    db.init_app(app)
    celery.conf.update(app.config)
    
    from .routes import notification_bp
    app.register_blueprint(notification_bp, url_prefix='/notifications')
    
    return app