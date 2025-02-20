"""
Middleware para el servicio de kiosks
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from Admin_Kiosk3_Backend.common.logging.logger import get_logger

log = get_logger('kiosk_middleware')

def admin_required():
    """Decorador para rutas que requieren rol de admin"""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get('role') != 'admin':
                log.warning(f"Access denied: User {claims.get('sub')} attempted admin action")
                return jsonify({
                    'status': 'error',
                    'message': 'Admin privileges required'
                }), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def operator_required():
    """Decorador para rutas que requieren rol de operador"""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get('role') not in ['admin', 'operator']:
                log.warning(f"Access denied: User {claims.get('sub')} attempted operator action")
                return jsonify({
                    'status': 'error',
                    'message': 'Operator privileges required'
                }), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper 