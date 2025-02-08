from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import Kiosk, db
import uuid

kiosk_bp = Blueprint('kiosk', __name__)

@kiosk_bp.route('/kiosks', methods=['POST'])
@jwt_required()
def create_kiosk():
    """Registrar un nuevo kiosko (genera un código QR único)"""
    current_user = get_jwt_identity()
    data = request.get_json() or {}
    # Generar un código único para el kiosko (por ejemplo UUID)
    kiosk_code = data.get('code') or str(uuid.uuid4())
    name = data.get('name', '')
    location = data.get('location', '')
    # Crear y guardar el kiosko
    kiosk = Kiosk(code=kiosk_code, name=name, location=location, assigned_to=None)
    db.session.add(kiosk)
    db.session.commit()
    return jsonify({'message': 'Kiosko creado', 'kiosk': {'id': kiosk.id, 'code': kiosk.code}}), 201

@kiosk_bp.route('/kiosks/<int:kiosk_id>', methods=['GET'])
@jwt_required()
def get_kiosk(kiosk_id):
    """Obtener información de un kiosko por ID"""
    kiosk = Kiosk.query.get_or_404(kiosk_id)
    result = {'id': kiosk.id, 'code': kiosk.code, 'name': kiosk.name, 'location': kiosk.location, 'assigned_to': kiosk.assigned_to}
    return jsonify(result), 200

@kiosk_bp.route('/kiosks/assign', methods=['POST'])
@jwt_required()
def assign_kiosk():
    """Asignar un kiosko a un usuario (p. ej., al escanear un código QR)"""
    current_user = get_jwt_identity()
    data = request.get_json()
    if not data or not data.get('code'):
        return jsonify({'message': 'Código de kiosko no proporcionado'}), 400
    kiosk = Kiosk.query.filter_by(code=data['code']).first()
    if not kiosk:
        return jsonify({'message': 'Kiosko no encontrado'}), 404
    # Asignar el kiosko al usuario actual (o podría ser a otra entidad según roles)
    kiosk.assigned_to = current_user
    db.session.commit()
    return jsonify({'message': f'Kiosko {kiosk.code} asignado al usuario {current_user}'}), 200

@kiosk_bp.route('/kiosks', methods=['GET'])
@jwt_required()
def list_kiosks():
    """Listar todos los kioskos (o los asignados al usuario actual, según rol)"""
    kiosks = Kiosk.query.all()
    result = []
    for k in kiosks:
        result.append({
            'id': k.id, 'code': k.code, 'name': k.name,
            'location': k.location, 'assigned_to': k.assigned_to
        })
    return jsonify(result), 200 