import os
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from Admin_Kiosk3_Backend.common.config import Config
from Admin_Kiosk3_Backend.common.logging.logger import get_logger
from Admin_Kiosk3_Backend.common import db, init_db
from flask_cors import CORS

log = get_logger('auth_service')

def create_app(config_class=None):
    """
    Factory de aplicación Flask para auth_service
    
    Args:
        config_class: Clase de configuración opcional
        
    Returns:
        Aplicación Flask configurada
    """
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
    
    # Cargar configuración
    if config_class is None:
        from .config import Config as ServiceConfig
        config_class = ServiceConfig
    
    app.config.from_object(config_class)
    
    # Inicializar extensiones
    init_db(app)
    Migrate(app, db)  # Inicializar Flask-Migrate
    jwt = JWTManager(app)
    
    # Registrar blueprint
    from .routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    # Configurar manejadores de error
    @app.errorhandler(404)
    def not_found_error(error):
        log.warning(f"Ruta no encontrada: {error}")
        return {'error': 'Recurso no encontrado'}, 404
        
    @app.errorhandler(500)
    def internal_error(error):
        log.error(f"Error interno del servidor: {error}")
        db.session.rollback()
        return {'error': 'Error interno del servidor'}, 500
    
    # Configurar hooks JWT
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        from .models import User
        identity = jwt_data["sub"]
        return User.query.filter_by(id=identity).one_or_none()
    
    @jwt.additional_claims_loader
    def add_claims_to_access_token(identity):
        from .models import User
        user = User.query.get(identity)
        return {
            "role": user.role,
            "email": user.email
        }
    
    # Configurar validaciones JWT
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        log.warning(f"Token inválido: {error}")
        return {"error": "Token inválido"}, 401
        
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        log.warning(f"Token expirado para usuario {jwt_payload.get('sub')}")
        return {"error": "Token expirado"}, 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        log.warning("Intento de acceso sin token")
        return {"error": "Token requerido"}, 401
    
    log.info(f"Auth Service iniciado en puerto {app.config['SERVICE_PORT']}")
    return app

app = create_app()

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=app.config['SERVICE_PORT']
    ) 