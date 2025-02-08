from flask_jwt_extended import create_access_token, verify_jwt_in_request, get_jwt
from functools import wraps
from flask import jsonify

def generate_token(user_id, additional_claims=None):
    """Generar token JWT"""
    if additional_claims is None:
        additional_claims = {}
    return create_access_token(identity=user_id, additional_claims=additional_claims)

def verify_token():
    """Verificar token JWT"""
    verify_jwt_in_request()
    return get_jwt()

def admin_required():
    """Decorador para rutas que requieren rol admin"""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") != "admin":
                return jsonify({"message": "Se requiere rol de administrador"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper 