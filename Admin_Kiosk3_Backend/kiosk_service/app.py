"""
Aplicación principal del servicio de kiosks
"""
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from Admin_Kiosk3_Backend.common import db
from Admin_Kiosk3_Backend.common.logging.logger import get_logger
from .config import Config
from .routes import kiosk_bp
from flask_cors import CORS
import os

log = get_logger('kiosk_service')

def create_app(config_class=Config):
    """Crear y configurar la aplicación Flask"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Asegurar que JWT usa la misma clave secreta que auth_service
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    
    # Inicializar extensiones
    db.init_app(app)
    jwt = JWTManager(app)
    migrate = Migrate(app, db)
    CORS(app)
    
    # Registrar blueprints
    app.register_blueprint(kiosk_bp, url_prefix='/api/kiosk')
    
    # Configurar error handlers
    @app.errorhandler(422)
    def handle_validation_error(err):
        log.error(f"Error de validación: {err}")
        return jsonify({
            'status': 'error',
            'message': 'Error de validación en la petición'
        }), 422
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['SERVICE_PORT'])