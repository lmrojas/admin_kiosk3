import os, datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from Admin_Kiosk3_Backend.common.config import Config
from Admin_Kiosk3_Backend.common.logging.logger import get_logger
from Admin_Kiosk3_Backend.payment_service.models import Payment, db

# (Opcional: integración con notificaciones/Celery)
# from celery import Celery
# celery = Celery(broker=os.environ.get('REDIS_URL', 'redis://redis:6379/0'))

app = Flask(__name__)
Config.init_app(app)
jwt = JWTManager(app)
log = get_logger('payment_service')

# Modelo de Pago/Transacción
class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)      # ID del usuario que realizó el pago
    kiosk_id = db.Column(db.Integer, nullable=False)     # ID del kiosko donde se realizó
    amount = db.Column(db.Numeric(10,2), nullable=False) # Monto del pago
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    status = db.Column(db.String(20), default='completed')  # estado del pago (completed, pending, etc.)

with app.app_context():
    db.create_all()

@app.route('/payments', methods=['POST'])
@jwt_required()
def create_payment():
    """Registrar un nuevo pago (p. ej., transacción realizada en un kiosko)"""
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    # Validar datos requeridos
    if not data.get('kiosk_id') or not data.get('amount'):
        return jsonify({'message': 'Faltan datos de la transacción'}), 400
    # Crear el registro de pago
    payment = Payment(user_id=user_id, kiosk_id=data['kiosk_id'], amount=data['amount'])
    db.session.add(payment)
    db.session.commit()
    # Opcional: desencadenar notificación asíncrona (email/SMS) y evento en WebSocket
    # notify_payment.delay(payment.id)  # Ejemplo: llamar tarea Celery (definida en notification_service)
    # socketio.emit('payment_update', { ... }, broadcast=True)  # Ejemplo: emitir evento en tiempo real
    return jsonify({
        'message': 'Pago registrado',
        'payment': {'id': payment.id, 'amount': str(payment.amount), 'kiosk_id': payment.kiosk_id, 'status': payment.status}
    }), 201

@app.route('/payments', methods=['GET'])
@jwt_required()
def list_payments():
    """Listar pagos (opción: filtrar por usuario actual o por rol administrador)"""
    current_user = get_jwt_identity()
    # Ejemplo: si no es admin, filtrar por usuario actual
    payments_query = Payment.query
    # (Podríamos usar claims de JWT para verificar si es admin y no filtrar)
    payments = payments_query.filter_by(user_id=current_user).all()
    result = []
    for p in payments:
        result.append({
            'id': p.id, 'user_id': p.user_id, 'kiosk_id': p.kiosk_id,
            'amount': str(p.amount), 'timestamp': p.timestamp.isoformat(), 'status': p.status
        })
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003) 