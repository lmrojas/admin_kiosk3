import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from Admin_Kiosk3_Backend.common.config import Config
from Admin_Kiosk3_Backend.common.logging.logger import get_logger
from Admin_Kiosk3_Backend.auth_service.models import User, db

app = Flask(__name__)
Config.init_app(app)
# Configuración de la app Flask
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://user:password@db:5432/admin_kiosk3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'super-secret-key')  # Clave JWT segura en entorno
db = SQLAlchemy(app)
jwt = JWTManager(app)
log = get_logger('auth_service')

# Modelo de Usuario con roles
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user')  # rol del usuario (e.g., admin, user)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Crear tablas (solo en entorno de desarrollo, en producción usar migraciones)
with app.app_context():
    db.create_all()

@app.route('/auth/register', methods=['POST'])
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

@app.route('/auth/login', methods=['POST'])
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

@app.route('/auth/users', methods=['GET'])
@jwt_required()  # Solo usuarios autenticados (ej. admin) pueden listar usuarios
def list_users():
    """Ejemplo de ruta protegida que lista usuarios (requiere rol admin)"""
    current_user_id = get_jwt_identity()
    # Opcional: verificar rol del usuario actual
    claims = request.jwt_validation_claims if hasattr(request, 'jwt_validation_claims') else None
    # Si quisiéramos forzar que solo admin pueda acceder:
    # if claims is None or claims.get('role') != 'admin':
    #     return jsonify({'message': 'Acceso no autorizado'}), 403
    users = User.query.all()
    result = [{'id': u.id, 'username': u.username, 'role': u.role} for u in users]
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001) 