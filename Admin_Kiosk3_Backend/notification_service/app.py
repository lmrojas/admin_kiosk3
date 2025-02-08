from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required
from Admin_Kiosk3_Backend.common.config import Config
from Admin_Kiosk3_Backend.common.logging.logger import get_logger
from Admin_Kiosk3_Backend.notification_service.models import Notification, db
import os
from celery import Celery

app = Flask(__name__)
Config.init_app(app)
jwt = JWTManager(app)
log = get_logger('notification_service')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://user:password@db:5432/admin_kiosk3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'super-secret-key')

# Configuración de Celery para tareas asíncronas
celery = Celery(
    'notification_service',
    broker=os.environ.get('REDIS_URL', 'redis://redis:6379/0')
)

db = SQLAlchemy(app)

@app.route('/notify/email', methods=['POST'])
@jwt_required()
def send_email():
    """Enviar notificación por email"""
    data = request.get_json()
    if not data or not data.get('to') or not data.get('subject'):
        return jsonify({'message': 'Datos incompletos'}), 400
    
    # Encolar tarea de envío de email
    send_email_task.delay(
        to=data['to'],
        subject=data['subject'],
        body=data.get('body', '')
    )
    return jsonify({'message': 'Email encolado para envío'}), 202

@celery.task
def send_email_task(to, subject, body):
    """Tarea Celery para envío asíncrono de email"""
    try:
        # Aquí iría la lógica real de envío de email (e.g., usando SMTP)
        print(f"Enviando email a {to}: {subject}")
        return True
    except Exception as e:
        print(f"Error enviando email: {str(e)}")
        return False

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006) 