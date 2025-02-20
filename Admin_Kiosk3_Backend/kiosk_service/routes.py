"""
Rutas del servicio de kiosks según reglas MDC
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from Admin_Kiosk3_Backend.common.logging.logger import get_logger
from .services import KioskService
from .middleware import admin_required, operator_required
from .config import Config
from .models import Kiosk

kiosk_bp = Blueprint('kiosk', __name__)
log = get_logger('kiosk_routes')

@kiosk_bp.route('/create', methods=['POST'])
@jwt_required()
@admin_required()
def create_kiosk():
    """
    Crear un nuevo kiosk
    ---
    tags:
      - Kiosks
    security:
      - Bearer: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - name
              - location
            properties:
              name:
                type: string
              location:
                type: string
              ip_address:
                type: string
              assigned_user_id:
                type: integer
    responses:
      201:
        description: Kiosk creado exitosamente
      400:
        description: Datos inválidos
      401:
        description: No autorizado
      500:
        description: Error del servidor
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400

        required = ['name', 'location']
        if not all(field in data for field in required):
            return jsonify({
                'status': 'error',
                'message': f'Required fields: {", ".join(required)}'
            }), 400

        current_user = get_jwt_identity()
        result = KioskService.create_kiosk(data, created_by=current_user)

        if result['status'] == 'error':
            return jsonify(result), 400

        log.info(f"Kiosk created successfully by user {current_user}")
        return jsonify(result), 201

    except Exception as e:
        log.error(f"Error creating kiosk: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@kiosk_bp.route('/list', methods=['GET'])
@jwt_required()
def list_kiosks():
    """
    Listar kiosks
    ---
    tags:
      - Kiosks
    security:
      - Bearer: []
    responses:
      200:
        description: Lista de kiosks
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  enum: [success, error]
                data:
                  type: array
                  items:
                    $ref: '#/components/schemas/Kiosk'
    """
    try:
        current_user = get_jwt_identity()
        log.info(f"Listing kiosks for user {current_user}")
        
        result = KioskService.list_kiosks()
        if result['status'] == 'success' and not isinstance(result['data'], list):
            result['data'] = [result['data']]
            
        return jsonify(result), 200
        
    except Exception as e:
        log.error(f"Error listing kiosks: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor'
        }), 500

@kiosk_bp.route('/<int:kiosk_id>', methods=['GET'])
@jwt_required()
def get_kiosk(kiosk_id):
    """
    Obtener detalles de un kiosk
    ---
    tags:
      - Kiosks
    security:
      - Bearer: []
    parameters:
      - in: path
        name: kiosk_id
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Detalles del kiosk
      404:
        description: Kiosk no encontrado
      401:
        description: No autorizado
      500:
        description: Error del servidor
    """
    try:
        result = KioskService.get_kiosk(kiosk_id)
        if result['status'] == 'error':
            return jsonify(result), 404

        return jsonify(result), 200

    except Exception as e:
        log.error(f"Error getting kiosk {kiosk_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

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