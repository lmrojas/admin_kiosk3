"""
Middleware de autenticación y autorización según reglas MDC
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from Admin_Kiosk3_Backend.common.logging.logger import get_logger

log = get_logger('auth_middleware')

def admin_required(fn):
    """
    Decorador que verifica rol de administrador
    
    Args:
        fn: Función a decorar
        
    Returns:
        Función decorada que verifica permisos de admin
    
    Example:
        @admin_required
        def admin_route():
            return "Solo admins pueden ver esto"
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get("role") != "admin":
            log.warning(f"Acceso denegado a ruta admin: {fn.__name__}")
            return jsonify(error="Se requieren permisos de administrador"), 403
        return fn(*args, **kwargs)
    return wrapper

def operator_required(fn):
    """
    Decorador que verifica rol de operador o superior
    
    Args:
        fn: Función a decorar
        
    Returns:
        Función decorada que verifica permisos de operador
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get("role") not in ["admin", "operator"]:
            log.warning(f"Acceso denegado a ruta de operador: {fn.__name__}")
            return jsonify(error="Se requieren permisos de operador"), 403
        return fn(*args, **kwargs)
    return wrapper

def role_required(allowed_roles):
    """
    Decorador que verifica roles permitidos
    
    Args:
        allowed_roles: Lista de roles permitidos
        
    Returns:
        Función decorada que verifica roles
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") not in allowed_roles:
                log.warning(
                    f"Acceso denegado a {fn.__name__}: rol {claims.get('role')} "
                    f"no está en {allowed_roles}"
                )
                return jsonify(error="Rol no autorizado"), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def active_user_required(fn):
    """
    Decorador que verifica que el usuario esté activo
    
    Args:
        fn: Función a decorar
        
    Returns:
        Función decorada que verifica estado activo
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if not claims.get("is_active", True):
            log.warning(f"Intento de acceso de usuario inactivo: {claims.get('sub')}")
            return jsonify(error="Usuario inactivo"), 403
        return fn(*args, **kwargs)
    return wrapper 