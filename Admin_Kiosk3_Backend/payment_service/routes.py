from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import Payment, db

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/payments', methods=['POST'])
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
    return jsonify({
        'message': 'Pago registrado',
        'payment': {'id': payment.id, 'amount': str(payment.amount), 'kiosk_id': payment.kiosk_id, 'status': payment.status}
    }), 201

@payment_bp.route('/payments', methods=['GET'])
@jwt_required()
def list_payments():
    """Listar pagos (opción: filtrar por usuario actual o por rol administrador)"""
    current_user = get_jwt_identity()
    payments = Payment.query.filter_by(user_id=current_user).all()
    result = []
    for p in payments:
        result.append({
            'id': p.id, 'user_id': p.user_id, 'kiosk_id': p.kiosk_id,
            'amount': str(p.amount), 'timestamp': p.timestamp.isoformat(), 'status': p.status
        })
    return jsonify(result), 200 