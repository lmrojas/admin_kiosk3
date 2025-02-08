from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_socketio import emit
from Admin_Kiosk3_Backend.common.logging.logger import get_logger
from Admin_Kiosk3_Backend.websocket_service.services import broadcast_message
from Admin_Kiosk3_Backend.websocket_service.models import WebSocketConnection, db

ws_bp = Blueprint('websocket', __name__)
log = get_logger('websocket_routes')

@ws_bp.route('/broadcast', methods=['POST'])
@jwt_required()
def broadcast():
    """Endpoint REST para enviar mensaje broadcast a todos los clientes"""
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'message': 'Datos de mensaje no proporcionados'}), 400
    
    if broadcast_message(data['message']):
        return jsonify({'message': 'Mensaje enviado'}), 200
    return jsonify({'message': 'Error enviando mensaje'}), 500

@ws_bp.route('/connections', methods=['GET'])
@jwt_required()
def get_connections():
    """Obtener estado de las conexiones WebSocket"""
    active_connections = WebSocketConnection.query.filter_by(status='active').all()
    return jsonify({
        'status': 'running',
        'active_connections': len(active_connections),
        'connections': [conn.to_dict() for conn in active_connections]
    }), 200 