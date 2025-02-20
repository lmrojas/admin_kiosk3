from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from Admin_Kiosk3_Backend.common.security.jwt_auth import generate_token
from Admin_Kiosk3_Backend.common.logging.logger import get_logger
from .models import User, Role, db

log = get_logger('auth_service')

class AuthService:
    """Servicio de autenticación según reglas MDC"""
    
    @staticmethod
    def create_user(
        username: str,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        role: str = 'operator'
    ) -> Optional[User]:
        """
        Crear un nuevo usuario
        
        Args:
            username: Nombre de usuario único
            email: Email único
            password: Contraseña (será hasheada)
            first_name: Nombre
            last_name: Apellido
            role: Rol del usuario (default: operator)
            
        Returns:
            User object o None si hay error
        """
        try:
            # Verificar si ya existe
            if User.query.filter_by(username=username).first():
                log.warning(f"Username ya existe: {username}")
                return None
                
            if User.query.filter_by(email=email).first():
                log.warning(f"Email ya existe: {email}")
                return None
            
            user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role=role
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            log.info(f"Usuario creado: {username}")
            return user
            
        except Exception as e:
            log.error(f"Error creando usuario: {str(e)}")
            db.session.rollback()
            return None

    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Autenticar usuario y generar tokens
        
        Args:
            username: Nombre de usuario
            password: Contraseña
            
        Returns:
            Dict con tokens y datos de usuario o None si falla
        """
        try:
            user = User.query.filter_by(username=username).first()
            
            if not user or not user.check_password(password):
                log.warning(f"Intento de login fallido: {username}")
                return None
                
            if not user.is_active:
                log.warning(f"Intento de login de usuario inactivo: {username}")
                return None
            
            # Actualizar último login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Generar token con claims
            additional_claims = {
                "role": user.role,
                "email": user.email
            }
            access_token = generate_token(user.id, additional_claims)
            
            log.info(f"Login exitoso: {username}")
            return {
                'access_token': access_token,
                'user': user.to_dict()
            }
            
        except Exception as e:
            log.error(f"Error en autenticación: {str(e)}")
            return None

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """Obtener usuario por ID"""
        try:
            user = User.query.get(user_id)
            return user.to_dict() if user else None
        except Exception as e:
            log.error(f"Error obteniendo usuario {user_id}: {str(e)}")
            return None

    @staticmethod
    def update_user(
        user_id: int,
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Actualizar datos de usuario
        
        Args:
            user_id: ID del usuario
            data: Dict con campos a actualizar
            
        Returns:
            Usuario actualizado o None si hay error
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return None
                
            # Actualizar campos permitidos
            allowed_fields = ['first_name', 'last_name', 'email', 'is_active']
            for field in allowed_fields:
                if field in data:
                    setattr(user, field, data[field])
            
            db.session.commit()
            return user.to_dict()
            
        except Exception as e:
            log.error(f"Error actualizando usuario {user_id}: {str(e)}")
            db.session.rollback()
            return None