from Admin_Kiosk3_Backend.common.security.jwt_auth import generate_token
from Admin_Kiosk3_Backend.common.logging.logger import get_logger
from .models import User, db

log = get_logger('auth_service')

class AuthService:
    @staticmethod
    def create_user(username, password, role='user'):
        """Crear un nuevo usuario"""
        user = User(username=username, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        log.info(f"Usuario creado: {username}")
        return user

    @staticmethod
    def authenticate_user(username, password):
        """Autenticar usuario y generar token JWT"""
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            log.warning(f"Intento de login fallido para usuario: {username}")
            return None
        
        additional_claims = {"role": user.role}
        access_token = generate_token(user.id, additional_claims)
        log.info(f"Login exitoso: {username}")
        return access_token, user