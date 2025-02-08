import os, uuid
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://user:password@db:5432/admin_kiosk3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'super-secret-key')
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Modelo de Kiosko
class Kiosk(db.Model):
    __tablename__ = 'kiosks'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(100), unique=True, nullable=False)  # Código QR o identificador único del kiosko
    name = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # usuario/admin asignado (opcional)

# Crear tabla de kioskos
with app.app_context():
    db.create_all()

@app.route('/kiosks', methods=['POST'])
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

@app.route('/kiosks/<int:kiosk_id>', methods=['GET'])
@jwt_required()
def get_kiosk(kiosk_id):
    """Obtener información de un kiosko por ID"""
    kiosk = Kiosk.query.get_or_404(kiosk_id)
    result = {'id': kiosk.id, 'code': kiosk.code, 'name': kiosk.name, 'location': kiosk.location, 'assigned_to': kiosk.assigned_to}
    return jsonify(result), 200

@app.route('/kiosks/assign', methods=['POST'])
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

@app.route('/kiosks', methods=['GET'])
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002) 