from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .models import db, User
from .services import AuthService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Registro de un nuevo usuario"""
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Datos incompletos'}), 400
    # Verificar si el usuario ya existe
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Usuario ya existe'}), 409
    # Crear nuevo usuario
    user = User(username=data['username'], role=data.get('role', 'user'))
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': f'Usuario {user.username} creado exitosamente'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """Autenticación de usuario y generación de JWT"""
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Credenciales no proporcionadas'}), 400
    user = User.query.filter_by(username=data['username']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Credenciales incorrectas'}), 401
    # Generar token de acceso JWT
    additional_claims = {"role": user.role}
    access_token = create_access_token(identity=user.id, additional_claims=additional_claims)
    return jsonify({
        'message': 'Inicio de sesión exitoso',
        'token': access_token,
        'user': {'id': user.id, 'username': user.username, 'role': user.role}
    }), 200

@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    """Ejemplo de ruta protegida que lista usuarios (requiere rol admin)"""
    current_user_id = get_jwt_identity()
    claims = request.jwt_validation_claims if hasattr(request, 'jwt_validation_claims') else None
    users = User.query.all()
    result = [{'id': u.id, 'username': u.username, 'role': u.role} for u in users]
    return jsonify(result), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    """Obtener perfil del usuario actual"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return jsonify(user.to_dict()) 