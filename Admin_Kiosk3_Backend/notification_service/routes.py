from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import Notification, db
from .services import send_notification

notification_bp = Blueprint('notification', __name__)

@notification_bp.route('/email', methods=['POST'])
@jwt_required()
def send_email():
    """Enviar notificación por email"""
    data = request.get_json()
    if not data or not data.get('to') or not data.get('subject'):
        return jsonify({'message': 'Datos incompletos'}), 400
    
    notification = Notification(
        user_id=get_jwt_identity(),
        type='email',
        content=f"To: {data['to']}\nSubject: {data['subject']}\nBody: {data.get('body', '')}"
    )
    db.session.add(notification)
    db.session.commit()
    
    # Encolar tarea asíncrona
    send_notification.delay(notification.id)
    return jsonify({'message': 'Notificación encolada', 'id': notification.id}), 202 