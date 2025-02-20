"""
Rutas del servicio de autenticación
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, create_access_token
from Admin_Kiosk3_Backend.common.logging.logger import get_logger
from .services import AuthService
from .middleware import admin_required, operator_required, active_user_required
from .models import User
from datetime import datetime
from Admin_Kiosk3_Backend.common import db

auth_bp = Blueprint('auth', __name__)
log = get_logger('auth_routes')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Endpoint de registro de usuarios"""
    try:
        data = request.get_json()
        required = ['username', 'email', 'password', 'first_name', 'last_name']
        
        if not data or not all(field in data for field in required):
            return jsonify({'error': 'Datos incompletos'}), 400
            
        user = AuthService.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=data.get('role', 'operator')
        )
        
        if not user:
            return jsonify({'error': 'No se pudo crear el usuario'}), 400
            
        log.info(f"Usuario registrado: {user.username}")
        return jsonify(user.to_dict()), 201
        
    except Exception as e:
        log.error(f"Error en registro: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint de autenticación"""
    try:
        username = request.json.get('username')
        password = request.json.get('password')
        
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return jsonify({
                'status': 'error',
                'message': 'Credenciales inválidas',
                'data': None
            }), 401
            
        access_token = create_access_token(identity=user.id)
        return jsonify({
            'status': 'success',
            'message': 'Login exitoso',
            'data': {
                'user': user.to_dict(),
                'token': access_token
            }
        }), 200
        
    except Exception as e:
        log.error(f"Error en login: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor',
            'data': None
        }), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
@active_user_required
def get_profile():
    """Obtener perfil del usuario actual"""
    try:
        user_id = get_jwt_identity()
        user = AuthService.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
            
        return jsonify(user), 200
        
    except Exception as e:
        log.error(f"Error obteniendo perfil: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@auth_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def list_users():
    """Listar usuarios (solo admin)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        users = User.query.paginate(
            page=page, 
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'total': users.total,
            'pages': users.pages,
            'current_page': users.page
        }), 200
        
    except Exception as e:
        log.error(f"Error listando usuarios: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@active_user_required
def update_user(user_id):
    """Actualizar datos de usuario"""
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        
        # Solo el propio usuario o un admin puede actualizar
        if current_user_id != user_id and claims.get('role') != 'admin':
            return jsonify({'error': 'No autorizado'}), 403
            
        data = request.get_json()
        result = AuthService.update_user(user_id, data)
        
        if not result:
            return jsonify({'error': 'Usuario no encontrado'}), 404
            
        log.info(f"Usuario {user_id} actualizado por {current_user_id}")
        return jsonify(result), 200
        
    except Exception as e:
        log.error(f"Error actualizando usuario: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@auth_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Verificar conexión a BD
        db.session.execute('SELECT 1')
        return {
            'status': 'healthy',
            'service': 'auth',
            'timestamp': datetime.utcnow().isoformat()
        }, 200
    except Exception as e:
        log.error(f"Health check falló: {str(e)}")
        return {
            'status': 'unhealthy',
            'service': 'auth',
            'error': str(e)
        }, 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Endpoint para logout
    ---
    tags:
      - Auth
    security:
      - Bearer: []
    responses:
      200:
        description: Logout exitoso
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  enum: [success]
                message:
                  type: string
    """
    try:
        current_user = get_jwt_identity()
        # Obtener el token actual
        jti = get_jwt()["jti"]
        # Aquí podrías agregar el token a una lista negra si lo necesitas
        
        log.info(f"Logout exitoso para usuario: {current_user}")
        return jsonify({
            'status': 'success',
            'message': 'Logged out successfully'
        }), 200
    except Exception as e:
        log.error(f'Error en logout: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': 'Error interno del servidor'
        }), 500 