import uuid
from datetime import datetime

def generate_id():
    """Generar ID único"""
    return str(uuid.uuid4())

def format_timestamp(timestamp):
    """Formatea timestamp para respuestas JSON"""
    return timestamp.isoformat() if timestamp else None

def validate_data(data, required_fields):
    """Validar campos requeridos en datos"""
    if not data:
        return False
    return all(field in data for field in required_fields)

def format_response(data, status_code=200):
    """Formatear respuesta API"""
    return {
        'data': data,
        'timestamp': datetime.utcnow().isoformat(),
        'status': status_code
    } 