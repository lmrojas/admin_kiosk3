from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def ai_access_required():
    """Decorador para rutas que requieren acceso a funciones de IA"""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") not in ["admin", "ai_manager"]:
                return jsonify({"msg": "Acceso denegado"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper