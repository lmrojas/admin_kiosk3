from flask import Flask
from flask_socketio import SocketIO, emit
from flask_jwt_extended import JWTManager
from Admin_Kiosk3_Backend.common.config import Config
from Admin_Kiosk3_Backend.common.logging.logger import get_logger

app = Flask(__name__)
Config.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")
jwt = JWTManager(app)
log = get_logger('websocket_service')

@socketio.on('connect')
def handle_connect():
    """Manejar nueva conexión WebSocket"""
    emit('connection_response', {'data': 'Conectado al servidor WebSocket'})

@socketio.on('kiosk_update')
def handle_kiosk_update(data):
    """Manejar actualización de estado de kiosko"""
    # Broadcast a todos los clientes conectados
    emit('kiosk_status', data, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    """Manejar desconexión de cliente"""
    print('Cliente desconectado')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5005) 