from flask_socketio import emit
from Admin_Kiosk3_Backend.common.logging.logger import get_logger
from Admin_Kiosk3_Backend.websocket_service.models import WebSocketConnection, db
import datetime

log = get_logger('websocket_service')

def broadcast_message(message, event_type='broadcast_message'):
    """Enviar mensaje a todos los clientes conectados"""
    try:
        emit(event_type, {'message': message}, broadcast=True, namespace='/')
        log.info(f"Mensaje broadcast enviado: {message}")
        return True
    except Exception as e:
        log.error(f"Error enviando broadcast: {str(e)}")
        return False

def register_connection(session_id, user_id=None):
    """Registrar nueva conexión WebSocket"""
    try:
        connection = WebSocketConnection(
            session_id=session_id,
            user_id=user_id
        )
        db.session.add(connection)
        db.session.commit()
        log.info(f"Nueva conexión registrada: {session_id}")
        return connection
    except Exception as e:
        log.error(f"Error registrando conexión: {str(e)}")
        return None

def close_connection(session_id):
    """Marcar conexión como cerrada"""
    connection = WebSocketConnection.query.filter_by(session_id=session_id).first()
    if connection:
        connection.status = 'disconnected'
        connection.disconnected_at = datetime.datetime.utcnow()
        db.session.commit()
        log.info(f"Conexión cerrada: {session_id}")
        return True
    return False

def get_connected_clients():
    """Obtener número de clientes conectados"""
    # En un caso real, esto podría consultar Redis para conexiones distribuidas
    return 'N/A' 