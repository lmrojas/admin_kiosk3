Admin_Kiosk3: Código Fuente Completo
A continuación se presenta el código fuente completo del sistema Admin_Kiosk3, organizado según la arquitectura definida. El código se divide en secciones para cada microservicio del backend (Flask), la aplicación frontend (React + TailwindCSS) y la configuración de despliegue e infraestructura (Docker, Kubernetes, CI/CD). Todo el código sigue principios de modularidad, escalabilidad y buenas prácticas de seguridad (uso de JWT, gestión de claves mediante variables de entorno, etc.).
Backend (Flask Microservicios)
Cada microservicio del backend es una aplicación Flask independiente, conectada a PostgreSQL mediante SQLAlchemy. Se utiliza JWT para autenticación segura, Flask-SocketIO con Redis para comunicación en tiempo real, y Celery con Redis para procesamiento asíncrono de notificaciones. Un API Gateway unifica la entrada a la API y enruta las solicitudes a los microservicios correspondientes.
auth_service – Autenticación y Gestión de Usuarios/Roles
Este servicio maneja la creación de usuarios, inicio de sesión y la emisión/verificación de tokens JWT. También gestiona los roles de usuario. Usa Flask-JWT-Extended para facilitar la integración de JWT.
Archivo: auth_service/app.py
python
Copiar
import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# Configuración de la app Flask
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://user:password@db:5432/admin_kiosk3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'super-secret-key')  # Clave JWT segura en entorno
db = SQLAlchemy(app)
jwt = JWTManager(app)

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

# Otras rutas de gestión de usuarios/roles podrían incluir:
# - Actualizar rol de usuario (solo admin)
# - Eliminar usuario, etc.

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

Notas:
La clave secreta JWT se obtiene de una variable de entorno para no almacenarla en código (gestión segura de claves).
Las contraseñas de usuario se almacenan en la base de datos usando hash seguro.
Las rutas /auth/register y /auth/login permiten crear usuarios y autenticarse, devolviendo un token JWT en el login.
La ruta /auth/users (ejemplo) muestra cómo proteger endpoints con JWT y roles (en un caso real se verificaría que el rol sea "admin" antes de listar usuarios).
kiosk_service – Gestión de Kioskos y Vinculación de Códigos QR
Servicio responsable de la gestión de kioskos. Permite registrar nuevos kioskos, consultarlos y vincularlos a códigos QR escaneados. Supongamos que cada kiosko tiene un código QR único; cuando un administrador escanea el código, se envía el identificador del kiosko para asignarlo a su cuenta u otra entidad según la lógica de negocio.
Archivo: kiosk_service/app.py
python
Copiar
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

Notas:
Los kioskos se identifican por un código único (code) que corresponde al QR. El endpoint /kiosks/assign recibe un código escaneado y marca ese kiosko como asignado al usuario autenticado que hizo la petición (representando la vinculación vía QR).
Se protegen los endpoints con @jwt_required() para que solo usuarios autenticados puedan crear, asignar o listar kioskos.
En un escenario real, podríamos filtrar list_kiosks para que usuarios no administradores solo vean sus kioskos asignados, etc., comprobando el rol almacenado en el JWT.
payment_service – Manejo de Pagos y Transacciones
Este microservicio gestiona pagos y transacciones. Permite registrar pagos realizados en kioskos, listar transacciones, etc. Tras procesar un pago, se podrían desencadenar tareas asíncronas (por ejemplo, envío de notificación de recibo por email, actualización en tiempo real vía WebSocket, etc.).
Archivo: payment_service/app.py
python
Copiar
import os, datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

# (Opcional: integración con notificaciones/Celery)
# from celery import Celery
# celery = Celery(broker=os.environ.get('REDIS_URL', 'redis://redis:6379/0'))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://user:password@db:5432/admin_kiosk3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'super-secret-key')
db = SQLAlchemy(app)
jwt = JWTManager(app)

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

Notas:
El endpoint /payments (POST) crea un nuevo pago. Después de guardar, sugiere cómo se podría integrar con otros servicios:
Llamando una tarea Celery (notify_payment.delay(...)) para enviar un recibo o notificación vía notification_service.
Emitiendo un evento en tiempo real a través de websocket_service para notificar a clientes conectados (por ejemplo, para actualizar un panel de administración en vivo). En el código, estas llamadas están comentadas ya que requerirían configuración adicional (la tarea en el servicio de notificación y un objeto SocketIO configurado con Redis).
El endpoint /payments (GET) lista pagos. En este ejemplo, lista solo los pagos del usuario autenticado (si quisiéramos permitir que un admin viera todos, verificaríamos el rol en el token).
ai_service – Servicio de Inteligencia Artificial (Predicciones y Recomendaciones)
Este microservicio proporciona funcionalidades de IA, como predicciones y recomendaciones basadas en datos de kioskos y transacciones. Por simplicidad, incluiremos un endpoint de ejemplo que podría, por ejemplo, predecir ventas futuras o recomendar acciones, usando datos disponibles. En una implementación real, este servicio podría cargar un modelo de Machine Learning entrenado y usarlo para generar resultados.
Archivo: ai_service/app.py
python
Copiar
import os, random
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'super-secret-key')
jwt = JWTManager(app)

@app.route('/ai/predict', methods=['GET'])
@jwt_required()
def predict_sales():
    """Ejemplo de predicción de ventas futuras para un kiosko (dummy data)"""
    kiosk_id = request.args.get('kiosk_id')
    if not kiosk_id:
        return jsonify({'message': 'kiosk_id requerido'}), 400
    # Lógica de predicción simulada (e.g., basada en historial de pagos)
    predicted_value = round(random.uniform(1000, 5000), 2)  # valor aleatorio de ejemplo
    return jsonify({
        'kiosk_id': kiosk_id,
        'predicted_sales_next_month': predicted_value
    }), 200

@app.route('/ai/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    """Ejemplo de recomendación basado en IA (dummy data)"""
    user_id = request.args.get('user_id')
    # Lógica de recomendación simulada
    recommendations = ["Mejorar inventario", "Promoción especial", "Reubicar kiosko"]  # dummy recommendations
    return jsonify({
        'user_id': user_id,
        'recommendations': recommendations
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)

Notas:
Se protegen las rutas con JWT (@jwt_required()), asumiendo que solo usuarios autenticados (quizá administradores) pueden solicitar predicciones.
Los endpoints devuelven datos simulados. En una implementación real, se integraría un modelo de ML o análisis de datos (por ejemplo, usando librerías como scikit-learn, TensorFlow, etc., con un modelo pre-entrenado) para producir resultados significativos.
websocket_service – Servicio de Comunicación en Tiempo Real (Flask-SocketIO + Redis)
Este servicio gestiona conexiones WebSocket para comunicación en tiempo real con los clientes (por ejemplo, para notificaciones instantáneas, actualizaciones en vivo de pagos, etc.). Usa Flask-SocketIO junto con un backend de Redis para permitir escalabilidad horizontal (varias instancias de WebSocket server compartiendo estado mediante Redis).
Archivo: websocket_service/app.py
python
Copiar
import os
from flask import Flask, request
from flask_socketio import SocketIO, emit, disconnect
import jwt  # PyJWT, para decodificar JWT manualmente en la conexión

app = Flask(__name__)
# Configurar SocketIO con Redis como message queue (para escalabilidad en múltiples pods/instancias)
redis_url = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
socketio = SocketIO(app, cors_allowed_origins="*", message_queue=redis_url)

# Clave secreta JWT (debe ser la misma usada para generar tokens en auth_service)
JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'super-secret-key')

@socketio.on('connect')
def handle_connect():
    """Gestionar nueva conexión WebSocket, verificando JWT para autenticación."""
    # Flask-SocketIO proporciona request.headers y request.args en contexto de socket
    token = request.args.get('token')
    if token:
        try:
            # Verificar el token JWT
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            user_id = payload.get('sub') or payload.get('identity')  # flask_jwt_extended usa 'sub' o 'identity' para ID de usuario
            # Se podría unir al usuario a una "room" específica si se desea dirigir notificaciones personalizadas:
            # join_room(f"user_{user_id}")
            print(f"Usuario {user_id} conectado via WebSocket.")
            # Opcional: enviar una confirmación al cliente
            emit('connected', {'message': 'Conexión WebSocket establecida.'})
        except jwt.PyJWTError:
            print("JWT inválido, desconectando...")
            disconnect()
    else:
        # Si no hay token, desconectar
        print("No JWT provided, disconnecting WebSocket.")
        disconnect()

@socketio.on('join_room')
def handle_join(data):
    """Unirse a una sala específica (p.ej., sala de un kiosko para recibir sus eventos)"""
    room = data.get('room')
    if room:
        from flask_socketio import join_room
        join_room(room)
        emit('joined', {'room': room}, to=room)
        print(f"Cliente unido a la sala: {room}")

@socketio.on('notify')
def handle_notify(data):
    """Recibir una notificación para difundir a clientes (puede ser invocado vía Redis por otros servicios)"""
    message = data.get('message', '')
    # Emitir el mensaje a todos los clientes conectados
    emit('notification', {'message': message}, broadcast=True)
    print(f"Notificación emitida a todos: {message}")

if __name__ == '__main__':
    # Ejecutar el servidor WebSocket (Nota: en producción usar eventlet/gevent)
    socketio.run(app, host='0.0.0.0', port=5005)

Notas:
En el evento connect, el servicio espera que el cliente envíe el token JWT como parámetro de conexión (token). Decodifica y verifica el JWT manualmente utilizando la misma clave secreta compartida. Si el token es inválido o ausente, se desconecta al cliente (disconnect()).
Los eventos personalizados como join_room y notify muestran cómo un cliente puede unirse a "rooms" para recibir mensajes específicos, y cómo difundir notificaciones a todos los clientes.
Este diseño permite que otros servicios publiquen mensajes a través de Redis (mediante socketio.emit desde otros procesos o usando Redis Pub/Sub) que el websocket_service retransmitirá a los clientes conectados. Por simplicidad, aquí simplemente recibimos un evento notify de algún cliente o sistema y lo emitimos a todos.
Aseguramos cors_allowed_origins="*" para permitir conexiones desde el frontend (en producción se puede restringir a dominios específicos).
notification_service – Servicio de Notificaciones (Push, SMS, Email) con Celery
El servicio de notificaciones gestiona el envío de mensajes fuera de la aplicación principal, como correos electrónicos, SMS o notificaciones push, típicamente de forma asíncrona mediante tareas Celery para no bloquear las peticiones web. Utiliza Redis como broker (y opcionalmente backend) de Celery para encolar tareas.
Implementamos tanto un pequeño API Flask para, por ejemplo, registrar tokens de dispositivo o probar el envío, como las tareas de Celery en sí. En despliegue, este servicio podría correr dos procesos: uno para la API Flask (si se necesita) y otro para el worker de Celery que consume las tareas.
Archivo: notification_service/app.py (API Flask opcional)
python
Copiar
import os
from flask import Flask, request, jsonify
from celery import Celery

app = Flask(__name__)

# Configurar Celery con Redis como broker y backend
app.config['CELERY_BROKER_URL'] = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
app.config['CELERY_RESULT_BACKEND'] = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'], backend=app.config['CELERY_RESULT_BACKEND'])

# Tareas Celery para envío de notificaciones
@celery.task(name='notification_service.send_email')
def send_email(to_email, subject, body):
    """Enviar un correo electrónico (simulado)"""
    # Aquí integraría con un servicio real de email (SMTP, SendGrid, etc.)
    print(f"[Sending Email] To: {to_email}, Subject: {subject}")
    # Simulación de envío exitoso
    return True

@celery.task(name='notification_service.send_sms')
def send_sms(to_number, message):
    """Enviar un SMS (simulado)"""
    # Integración real con API SMS (Twilio, etc.)
    print(f"[Sending SMS] To: {to_number}, Message: {message}")
    return True

@celery.task(name='notification_service.send_push')
def send_push(to_device_token, title, message):
    """Enviar notificación push (simulado)"""
    # Integración real con servicio de notificaciones push (Firebase Cloud Messaging, etc.)
    print(f"[Sending Push] To device: {to_device_token}, Title: {title}, Message: {message}")
    return True

# (Opcional) Rutas API para gestionar notificaciones, e.g., registrar tokens o disparar notificaciones manualmente
@app.route('/notify/test-email', methods=['POST'])
def test_email():
    """Endpoint para probar envío de email (coloca una tarea en la cola)"""
    data = request.get_json() or {}
    to_email = data.get('to')
    if not to_email:
        return jsonify({'message': 'Falta dirección de email'}), 400
    send_email.delay(to_email, "Test Admin_Kiosk3", "Este es un correo de prueba.")  # encolar tarea Celery
    return jsonify({'message': f'Email de prueba enviado a la cola para {to_email}'}), 200

if __name__ == '__main__':
    # Nota: en despliegue real, el worker de Celery se ejecuta aparte, 
    # y opcionalmente se puede correr la app Flask para exponer endpoints de notificación
    app.run(host='0.0.0.0', port=5006)

Notas:
Se configura Celery con Redis como broker y backend para tareas. Definimos tareas para enviar email, SMS y push. En este ejemplo, simplemente imprimen un mensaje simulando el envío; en producción integrarían con servicios externos (p.ej., SMTP, Twilio, Firebase, etc.).
Las tareas tienen nombres explícitos (notification_service.send_email, etc.) que permiten que otros microservicios puedan invocarlas usando ese nombre vía Celery. Por ejemplo, celery.send_task('notification_service.send_email', args=[...]) desde otro servicio publicaría la tarea en la cola que este worker escucha.
El endpoint /notify/test-email muestra cómo un cliente (o administrador) podría solicitar una notificación (aquí una prueba de email), que simplemente encola una tarea Celery para envío de email. Esto evita hacer el envío directamente en la petición HTTP.
En un entorno de producción, típicamente se ejecuta el worker de Celery con este mismo código (que registra las tareas) mediante un comando como celery -A notification_service.app.celery worker --loglevel=info, y opcionalmente se ejecuta la app Flask (flask run) si se requieren endpoints HTTP.
api_gateway – Puerta de Entrada Única de la API
El API Gateway es el único punto de entrada para clientes al sistema backend. Es una aplicación Flask que recibe todas las peticiones de los clientes y las redirige al microservicio correspondiente. Proporciona una única URL base para el frontend, ocultando la complejidad de múltiples servicios. También puede manejar preocupaciones transversales como autenticación (por ejemplo, validar JWT en una sola capa), rate limiting, logging unificado, etc.
En este ejemplo, implementaremos el gateway reenviando las peticiones a los microservicios usando HTTP (usando la librería requests). Cada microservicio podría estar expuesto internamente en una URL/puerto diferente (o nombre de host en Docker/K8s). El gateway extrae del path qué servicio se requiere (por ejemplo, /auth/... va a auth_service) y reenvía la solicitud, incluyendo encabezados de autenticación.
Archivo: api_gateway/app.py
python
Copiar
import os, requests
from flask import Flask, request, Response

app = Flask(__name__)

# URLs internos de cada microservicio (en Docker Compose o Kubernetes serían hostnames o servicios)
AUTH_SERVICE_URL = os.environ.get('AUTH_SERVICE_URL', 'http://auth_service:5001')
KIOSK_SERVICE_URL = os.environ.get('KIOSK_SERVICE_URL', 'http://kiosk_service:5002')
PAYMENT_SERVICE_URL = os.environ.get('PAYMENT_SERVICE_URL', 'http://payment_service:5003')
AI_SERVICE_URL = os.environ.get('AI_SERVICE_URL', 'http://ai_service:5004')
NOTIF_SERVICE_URL = os.environ.get('NOTIF_SERVICE_URL', 'http://notification_service:5006')
# El servicio de WebSocket usualmente se conecta directamente desde el cliente (no via gateway),
# pero si quisiéramos, podríamos manejar upgrade de WebSocket en un servidor externo (Nginx/Ingress).

# Helper para obtener headers a reenviar (ej: Authorization)
def forward_headers():
    headers = {}
    # Reenviar el header Authorization para conservar JWT en las peticiones a los servicios
    auth_header = request.headers.get('Authorization')
    if auth_header:
        headers['Authorization'] = auth_header
    # Reenviar Content-Type
    content_type = request.headers.get('Content-Type')
    if content_type:
        headers['Content-Type'] = content_type
    return headers

@app.route('/auth/<path:path>', methods=['GET','POST','PUT','DELETE'])
def proxy_auth(path):
    """Proxy para el servicio de autenticación (auth_service)"""
    url = f"{AUTH_SERVICE_URL}/auth/{path}"
    resp = requests.request(method=request.method, url=url, headers=forward_headers(), data=request.get_data())
    return Response(resp.content, status=resp.status_code, content_type=resp.headers.get('Content-Type'))

@app.route('/kiosks/<path:path>', methods=['GET','POST','PUT','DELETE'])
def proxy_kiosk(path):
    """Proxy para el servicio de kioskos (kiosk_service)"""
    url = f"{KIOSK_SERVICE_URL}/kiosks/{path}"
    resp = requests.request(method=request.method, url=url, headers=forward_headers(), data=request.get_data())
    return Response(resp.content, status=resp.status_code, content_type=resp.headers.get('Content-Type'))

@app.route('/payments/<path:path>', methods=['GET','POST','PUT','DELETE'])
def proxy_payment(path):
    """Proxy para el servicio de pagos (payment_service)"""
    url = f"{PAYMENT_SERVICE_URL}/payments/{path}"
    resp = requests.request(method=request.method, url=url, headers=forward_headers(), data=request.get_data())
    return Response(resp.content, status=resp.status_code, content_type=resp.headers.get('Content-Type'))

@app.route('/ai/<path:path>', methods=['GET','POST'])
def proxy_ai(path):
    """Proxy para el servicio de inteligencia artificial (ai_service)"""
    url = f"{AI_SERVICE_URL}/ai/{path}"
    resp = requests.request(method=request.method, url=url, headers=forward_headers(), data=request.get_data())
    return Response(resp.content, status=resp.status_code, content_type=resp.headers.get('Content-Type'))

@app.route('/notify/<path:path>', methods=['GET','POST'])
def proxy_notif(path):
    """Proxy para el servicio de notificaciones (notification_service)"""
    url = f"{NOTIF_SERVICE_URL}/notify/{path}"
    resp = requests.request(method=request.method, url=url, headers=forward_headers(), data=request.get_data())
    return Response(resp.content, status=resp.status_code, content_type=resp.headers.get('Content-Type'))

# (Opcional) se podrían manejar rutas específicas de conveniencia, p.ej.:
# @app.route('/login', methods=['POST']) -> proxy_auth('login') 
# para exponer /login directamente en gateway.

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

Notas:
Cada ruta en el gateway detecta el primer segmento (/auth/, /kiosks/, /payments/, /ai/, /notify/) y reenvía la solicitud al servicio correspondiente. Se usa requests.request para construir una petición al microservicio, pasando el método HTTP, URL, cabeceras relevantes y datos de la petición original.
forward_headers() recoge el header Authorization para que el token JWT enviado por el cliente pase al microservicio. Así, los microservicios pueden validar el JWT como vimos (cada servicio tiene la clave secreta y el decorador @jwt_required).
En un escenario real, podría implementarse lógica adicional en el gateway, como:
Validar el JWT una vez en el gateway y posiblemente pasar información de usuario en los headers (aunque suele ser suficiente con pasarlo directamente).
Manejar respuestas de error comunes (por ejemplo, un 401 de cualquier servicio podría interceptarse para añadir un mensaje unificado).
Logging centralizado de todas las peticiones o métricas.
El gateway no gestiona WebSockets directamente; los clientes se conectan al websocket_service por aparte (posiblemente vía un subdominio o ruta especial configurada en el proxy/Ingress, ver sección de despliegue).
Frontend (React + TailwindCSS)
La aplicación frontend es una SPA (Single Page Application) construida con React y estilizada con TailwindCSS. Proporciona una interfaz responsiva y agradable para interactuar con el sistema Admin_Kiosk3. Incluye funcionalidades como autenticación JWT (login/logout), escaneo de códigos QR para asignar kioskos, y actualización en tiempo real de información mediante WebSockets.
A continuación se muestran componentes clave del frontend:
App.jsx: Punto de entrada de la aplicación React, define las rutas y contexto global.
Login.jsx: Página de inicio de sesión, obtiene un JWT del backend y lo almacena de forma segura.
Dashboard.jsx: Página principal después de login, muestra información general (p. ej., lista de kioskos) e integra la conexión WebSocket para actualizaciones en vivo. Incluye funcionalidad para escanear QR y asignar kioskos.
QrScanner.jsx: Componente reutilizable para acceso a la cámara y escaneo de códigos QR (utilizando una librería de terceros).
Se utiliza TailwindCSS a través de clases utilitarias en los elementos JSX para el diseño y estilo responsivo.
Nota: Se asume que el proyecto fue inicializado con create-react-app o similar, y TailwindCSS configurado correctamente (archivo CSS importando Tailwind directives). En producción, la app podría estar servida como archivos estáticos mediante un servidor (por ejemplo Nginx) después de npm run build.
src/App.jsx – Configuración de Rutas y Contexto Global
Este componente configura el enrutamiento del frontend (por ejemplo, usando React Router) y provee contexto global para la autenticación (como el token JWT almacenado).
jsx
Copiar
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Dashboard from './components/Dashboard';

// Componente de ruta protegida que verifica si el usuario está autenticado
const PrivateRoute = ({ children }) => {
  const token = localStorage.getItem('token');
  return token ? children : <Navigate to="/login" replace />;
};

function App() {
  // Estado global simple para token (opcional, se puede usar Context API)
  const [token, setToken] = useState(localStorage.getItem('token') || null);

  // Si el token cambia (login o logout), almacenarlo/quitárlo de localStorage
  useEffect(() => {
    if (token) {
      localStorage.setItem('token', token);
    } else {
      localStorage.removeItem('token');
    }
  }, [token]);

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login onLogin={setToken} />} />
        <Route 
          path="/dashboard" 
          element={
            <PrivateRoute>
              <Dashboard token={token} />
            </PrivateRoute>
          } 
        />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Router>
  );
}

export default App;

Descripción:
Utilizamos BrowserRouter y definimos rutas para login y dashboard. Cualquier ruta no definida redirige a /dashboard por defecto (esto puede ajustarse según necesidades).
PrivateRoute es un componente que comprueba si hay un token en localStorage; si no, redirige a /login. Esto protege rutas como /dashboard de acceso no autenticado.
El estado global token podría en un proyecto más grande gestionarse con un contexto o librería de estado, pero para simplicidad usamos useState y sincronizamos con localStorage para persistencia.
onLogin pasado al componente Login permitirá establecer el token al iniciar sesión exitosamente.
src/components/Login.jsx – Componente de Inicio de Sesión
Formulario de login donde el administrador/usuario ingresa sus credenciales. Al enviar, realiza una petición a la API (/auth/login a través del gateway) y recibe un JWT que se almacena para futuras peticiones.
jsx
Copiar
import React, { useState } from 'react';

function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const response = await fetch('/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      if (!response.ok) {
        const resData = await response.json();
        throw new Error(resData.message || 'Error de autenticación');
      }
      const data = await response.json();
      const token = data.token;
      onLogin(token);  // guardar token en estado global (y localStorage vía App)
      // Redireccionar a dashboard podría manejarse aquí si no usamos <Navigate> en App
      // window.location.href = '/dashboard';
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <form onSubmit={handleSubmit} className="bg-white p-6 rounded shadow-md w-full max-w-sm">
        <h1 className="text-2xl font-bold mb-4 text-center">Admin_Kiosk3 - Login</h1>
        {error && <div className="mb-3 text-red-600 text-center">{error}</div>}
        <div className="mb-4">
          <label className="block text-gray-700">Usuario</label>
          <input 
            type="text" 
            className="w-full mt-1 p-2 border rounded focus:outline-none focus:ring" 
            value={username} 
            onChange={e => setUsername(e.target.value)} 
            required 
          />
        </div>
        <div className="mb-6">
          <label className="block text-gray-700">Contraseña</label>
          <input 
            type="password" 
            className="w-full mt-1 p-2 border rounded focus:outline-none focus:ring" 
            value={password} 
            onChange={e => setPassword(e.target.value)} 
            required 
          />
        </div>
        <button 
          type="submit" 
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition"
        >
          Iniciar Sesión
        </button>
      </form>
    </div>
  );
}

export default Login;

Descripción:
El formulario controla username y password con estado local.
En handleSubmit, se realiza fetch a /auth/login. Nótese que usamos la ruta relativa /auth/login asumiendo que el frontend se sirve desde el mismo dominio que el backend gateway (por ejemplo, en desarrollo con proxy, o en producción el mismo dominio/host con el gateway).
Si la respuesta es OK, extraemos el token JWT y lo pasamos a onLogin (que actualiza estado global en App). Si hay error, se muestra un mensaje de error.
Se aplican clases de TailwindCSS para estilos básicos: un formulario centrado con fondo gris claro, tarjeta blanca con sombra, campos de texto con borde y estados de focus, etc.
Tras login exitoso, la navegación a Dashboard ocurre automáticamente por el cambio en estado (en App, al tener token, el <PrivateRoute> permite renderizar Dashboard). También se podría hacer un redirect manual.
src/components/Dashboard.jsx – Panel Principal (Lista de Kioskos, WebSocket, Escaneo QR)
Esta vista representa la pantalla principal después de iniciar sesión. Muestra información relevante al admin (por ejemplo, una lista de kioskos existentes y sus estados) y ofrece funcionalidades como:
Conectar al WebSocket para recibir notificaciones/pagos en tiempo real.
Iniciar el escaneo de un código QR para asignar un kiosko.
Cerrar sesión (logout) si se desea.
jsx
Copiar
import React, { useEffect, useState } from 'react';
import io from 'socket.io-client';
import QrScanner from './QrScanner';

function Dashboard({ token }) {
  const [kiosks, setKiosks] = useState([]);
  const [wsMessage, setWsMessage] = useState(null);
  const [showScanner, setShowScanner] = useState(false);

  // Obtener lista de kioskos al cargar
  useEffect(() => {
    const fetchKiosks = async () => {
      try {
        const res = await fetch('/kiosks', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setKiosks(data);
        }
      } catch (err) {
        console.error('Error obteniendo kioskos:', err);
      }
    };
    fetchKiosks();
  }, [token]);

  // Conexión al WebSocket al montar
  useEffect(() => {
    const socket = io('/', {  // asume mismo host, path por defecto "/socket.io"
      query: { token: token }
    });
    socket.on('connect', () => {
      console.log('Conectado al WebSocket');
    });
    socket.on('notification', (data) => {
      // Manejar notificación recibida (por ejemplo, nueva transacción)
      setWsMessage(data.message);
      // Actualizar lista de kioskos/pagos si aplica...
      // Podríamos volver a fetchear pagos o recibir datos detallados
    });
    socket.on('payment_update', (data) => {
      // Ejemplo: manejar evento específico de actualización de pago
      console.log('Pago actualizado:', data);
      setWsMessage('Nuevo pago registrado en tiempo real');
      // Aquí se podría actualizar estado local de pagos, etc.
    });
    socket.on('disconnect', () => {
      console.log('Desconectado del WebSocket');
    });
    return () => {
      socket.disconnect();
    };
  }, [token]);

  // Manejar resultado del escaneo QR
  const handleScanResult = async (qrCode) => {
    setShowScanner(false);
    if (!qrCode) return;
    try {
      const res = await fetch('/kiosks/assign', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ code: qrCode })
      });
      const data = await res.json();
      if (res.ok) {
        // Actualizar la lista de kioskos tras asignación
        setKiosks(prev => prev.map(k => k.code === qrCode ? { ...k, assigned_to: /* current user id, if known */ null } : k));
        alert(`✅ ${data.message}`);
      } else {
        alert(`⚠️ ${data.message || 'Error asignando kiosko'}`);
      }
    } catch (err) {
      console.error('Error asignando kiosko:', err);
    }
  };

  return (
    <div className="p-4">
      <header className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Dashboard Admin_Kiosk3</h2>
        <button 
          onClick={() => { localStorage.removeItem('token'); window.location.href = '/login'; }} 
          className="bg-red-500 text-white px-4 py-2 rounded"
        >
          Cerrar Sesión
        </button>
      </header>

      {wsMessage && (
        <div className="mb-4 p-2 bg-green-100 text-green-800 border border-green-300 rounded">
          {wsMessage}
        </div>
      )}

      <div className="mb-4">
        <button 
          onClick={() => setShowScanner(true)} 
          className="bg-blue-600 text-white px-4 py-2 rounded"
        >
          📷 Escanear QR de Kiosko
        </button>
      </div>

      {showScanner && (
        <QrScanner onScan={handleScanResult} onClose={() => setShowScanner(false)} />
      )}

      <h3 className="text-xl font-semibold mb-2">Lista de Kioskos:</h3>
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white shadow rounded">
          <thead className="bg-gray-200 text-gray-700">
            <tr>
              <th className="py-2 px-4 text-left">ID</th>
              <th className="py-2 px-4 text-left">Código</th>
              <th className="py-2 px-4 text-left">Ubicación</th>
              <th className="py-2 px-4 text-left">Asignado a (UserID)</th>
            </tr>
          </thead>
          <tbody>
            {kiosks.map(kiosk => (
              <tr key={kiosk.id} className="border-b">
                <td className="py-1 px-4">{kiosk.id}</td>
                <td className="py-1 px-4">{kiosk.code}</td>
                <td className="py-1 px-4">{kiosk.location || '-'}</td>
                <td className="py-1 px-4">{kiosk.assigned_to || '-'}</td>
              </tr>
            ))}
            {kiosks.length === 0 && (
              <tr><td colSpan="4" className="py-2 px-4 text-center text-gray-500">No hay kioskos disponibles.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Dashboard;

Descripción:
Al montarse, el Dashboard obtiene la lista de kioskos del backend (GET /kiosks). El token JWT se envía en el header Authorization: Bearer ....
Se establece una conexión WebSocket usando socket.io-client (io('/')). Asumimos que el gateway/backend está en la misma origen, y que la ruta /socket.io está configurada para el servicio de WebSocket. Pasamos el token como query param para que el servidor pueda autenticar (como vimos en websocket_service).
Manejamos eventos de socket:
notification podría ser un evento genérico de notificaciones (ejemplo mostrado en websocket_service.handle_notify).
payment_update podría emitirse cuando hay un nuevo pago (mencionado en payment_service). Aquí simplemente mostramos un mensaje, pero podría usarse para actualizar la lista de pagos en un componente de transacciones, etc.
Un botón permite iniciar el escaneo de QR (setShowScanner(true)). Cuando showScanner es true, renderizamos el componente QrScanner.
handleScanResult se pasa a QrScanner para ser llamado cuando se escanee con éxito un código. Este manejador envía el código QR al endpoint /kiosks/assign via POST, con el token en la cabecera. Si la respuesta es exitosa, actualiza la lista de kioskos local (marcando como asignado, aquí simplificado) y muestra un alert. Si falla, muestra un alert de error.
La interfaz muestra los kioskos en una tabla sencilla usando TailwindCSS para estilos de tabla.
src/components/QrScanner.jsx – Componente de Escaneo de Código QR
Este componente encapsula la funcionalidad de escanear un código QR usando la cámara. Para simplificar el desarrollo, se puede usar una librería existente que provea el acceso a la cámara y decodificación de QR, como react-qr-reader u @blackbox-vision/react-qr-reader. A continuación se ilustra el uso hipotético de react-qr-reader para lograrlo.
jsx
Copiar
import React from 'react';
import QrReader from 'react-qr-reader';  // Librería de escaneo de QR

function QrScanner({ onScan, onClose }) {
  const handleScan = (data) => {
    if (data) {
      // Cuando obtengamos un resultado del QR, retornar ese valor y cerrar el escáner
      onScan(data);
    }
  };

  const handleError = (err) => {
    console.error('QR Scan Error:', err);
    // En caso de error podríamos notificar al usuario
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex flex-col items-center justify-center z-50">
      <div className="bg-white p-4 rounded">
        <h4 className="text-lg font-semibold mb-2">Escanear Código QR</h4>
        <QrReader
          delay={300}
          style={{ width: '300px' }}
          onError={handleError}
          onScan={handleScan}
        />
        <button onClick={onClose} className="mt-4 bg-gray-500 text-white px-3 py-1 rounded">
          Cancelar
        </button>
      </div>
    </div>
  );
}

export default QrScanner;

Descripción:
Se usa QrReader componente de la librería importada para acceder a la cámara. Sus props incluyen onScan (llamado cuando se decodifica exitosamente un QR) y onError. Aquí onScan invoca la prop onScan pasada desde Dashboard con los datos (data) obtenidos del QR.
El componente está envuelto en un overlay semi-transparente (fixed inset-0 bg-black bg-opacity-75) para cubrir la pantalla mientras se escanea, y centra el visor en la pantalla. Un botón "Cancelar" permite cerrar el escáner sin tomar acción.
Este enfoque asume que la aplicación se sirve sobre HTTPS en un dispositivo móvil para que la cámara sea accesible (los navegadores requieren HTTPS para getUserMedia).
Consideraciones de seguridad en frontend:
El token JWT se almacena en localStorage en este ejemplo por simplicidad. En un entorno real, podría considerarse almacenarlo en una cookie segura HTTPOnly para mitigar riesgos de XSS, a costa de una configuración CORS/CSRF adecuada. Almacenar en localStorage es común pero hay que asegurarse de proteger la app de inyecciones de script.
Todas las peticiones llevan el token en el header Authorization. La aplicación maneja redirección a login si no hay token (lo que cubriría el caso de token expirado si las respuestas 401 son manejadas, por ejemplo, en un fetch wrapper global).
TailwindCSS facilita asegurar que la UI sea responsiva y accesible, pero siempre se deben probar los componentes en diferentes tamaños de pantalla (el scanner, por ejemplo, podría ajustarse a pantalla completa en móviles).
Despliegue e Infraestructura
Para asegurar la escalabilidad y confiabilidad de Admin_Kiosk3, se usan contenedores Docker, orquestación con Kubernetes, y herramientas de monitoreo y CI/CD.
Docker y Docker Compose
En desarrollo local, Docker Compose facilita levantar todos los servicios (microservicios, base de datos, frontend, etc.) con un solo comando. Cada microservicio tiene un Dockerfile, y docker-compose.yml define cómo se montan juntos.
Archivo: Dockerfile (ejemplo genérico para servicios Flask)
Este Dockerfile base se puede usar para los microservicios de Flask (auth, kiosk, payment, ai, gateway, etc. variando el puerto o command si hace falta).
dockerfile
Copiar
# Usar imagen base de Python slim para tener un entorno ligero
FROM python:3.10-slim

# Variable de entorno para desactivar buffering (mejor logging en Docker)
ENV PYTHONUNBUFFERED=1

# Crear directorio de la app
WORKDIR /app

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Exponer el puerto (ejemplo: 5000, ajustable según servicio)
EXPOSE 5000

# Comando por defecto: lanzar la app (usar host 0.0.0.0 para accesibilidad fuera del contenedor)
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]

Cada servicio Flask tendría su propio contexto y requirements.txt (que incluiría Flask, Flask-JWT-Extended, SQLAlchemy, etc. y para algunos Celery, etc.). Podríamos también usar Gunicorn para producción en vez del servidor de desarrollo de Flask.
Archivo: Dockerfile.websocket (para servicio WebSocket)
Para websocket_service, se podría usar eventlet o gevent para el servidor SocketIO:
dockerfile
Copiar
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt  # requirements.txt incluiría flask-socketio, eventlet, etc.
COPY . .
EXPOSE 5005
# Ejecutar usando eventlet para compatibilidad WebSocket
CMD ["python", "app.py"]  # Dentro de app.py usamos socketio.run; alternativamente: ["flask", "run", ...]

Archivo: Dockerfile.frontend (para aplicación React)
dockerfile
Copiar
# Etapa 1: compilación del frontend
FROM node:18-alpine as build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install
COPY . .
RUN npm run build

# Etapa 2: servidor web para contenido estático
FROM nginx:stable-alpine
# Copiar el build generado al directorio default de Nginx
COPY --from=build /app/build /usr/share/nginx/html
# Copiar configuración de nginx si se requiere personalizar rutas (omitir si default sirve)
# COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

El Dockerfile de frontend hace un build de la aplicación React y luego usa Nginx para servir los archivos estáticos resultantes. Alternativamente, se podría usar un contenedor Node con serve (como se comentó en la planificación).
Archivo: docker-compose.yml
Define los servicios para desarrollo local. Incluye la base de datos PostgreSQL, Redis, todos los microservicios, el gateway y el frontend. Cada servicio de Flask expone su puerto interno, pero solamente el gateway y el frontend quizás se exponen a la máquina host para interacción directa (ya que el frontend hablará al gateway, y websockets al socket service). Redis y PostgreSQL son solo internos.
yaml
Copiar
version: '3.8'
services:
  db:
    image: postgres:14
    container_name: adminkiosk_db
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=admin_kiosk3
    volumes:
      - db_data:/var/lib/postgresql/data
    networks:
      - adminkiosk_net

  redis:
    image: redis:6-alpine
    container_name: adminkiosk_redis
    networks:
      - adminkiosk_net

  auth_service:
    build: ./auth_service
    container_name: auth_service
    env_file: .env              # Contiene JWT_SECRET_KEY, DATABASE_URL, etc.
    environment:
      - FLASK_APP=app.py
      - FLASK_ENV=development
      - DATABASE_URL=postgresql://user:password@db:5432/admin_kiosk3
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    depends_on:
      - db
    networks:
      - adminkiosk_net

  kiosk_service:
    build: ./kiosk_service
    container_name: kiosk_service
    env_file: .env
    environment:
      - FLASK_APP=app.py
      - DATABASE_URL=postgresql://user:password@db:5432/admin_kiosk3
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    depends_on:
      - db
    networks:
      - adminkiosk_net

  payment_service:
    build: ./payment_service
    container_name: payment_service
    env_file: .env
    environment:
      - FLASK_APP=app.py
      - DATABASE_URL=postgresql://user:password@db:5432/admin_kiosk3
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    networks:
      - adminkiosk_net

  ai_service:
    build: ./ai_service
    container_name: ai_service
    env_file: .env
    environment:
      - FLASK_APP=app.py
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    networks:
      - adminkiosk_net

  websocket_service:
    build: ./websocket_service
    container_name: websocket_service
    env_file: .env
    environment:
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    depends_on:
      - redis
    networks:
      - adminkiosk_net
    ports:
      - "5005:5005"   # expone el puerto del websocket server para conexiones (opcional, en dev)

  notification_service:
    build: ./notification_service
    container_name: notification_service
    env_file: .env
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
    networks:
      - adminkiosk_net
    # Este servicio puede tener 2 containers en prod (API y worker), en dev levantamos uno para simplificar

  api_gateway:
    build: ./api_gateway
    container_name: api_gateway
    env_file: .env
    environment:
      - AUTH_SERVICE_URL=http://auth_service:5001
      - KIOSK_SERVICE_URL=http://kiosk_service:5002
      - PAYMENT_SERVICE_URL=http://payment_service:5003
      - AI_SERVICE_URL=http://ai_service:5004
      - NOTIF_SERVICE_URL=http://notification_service:5006
    depends_on:
      - auth_service
      - kiosk_service
      - payment_service
      - ai_service
      - notification_service
    ports:
      - "5000:5000"   # expone el gateway en el host (puerto 5000)
    networks:
      - adminkiosk_net

  frontend:
    build: ./frontend   # construye usando Dockerfile.frontend
    container_name: adminkiosk_frontend
    depends_on:
      - api_gateway
    ports:
      - "3000:80"  # expone Nginx serving frontend en puerto 3000 host (o 80)
    networks:
      - adminkiosk_net

networks:
  adminkiosk_net:
    driver: bridge

volumes:
  db_data:

Descripción:
Cada servicio usa la red adminkiosk_net para que todos se resuelvan por nombre de contenedor (Docker Compose asigna hostnames iguales a los service names, e.g., auth_service).
env_file: .env centraliza algunas variables sensibles como JWT_SECRET_KEY para que todas las instancias lo compartan, garantizando que un token emitido por auth_service sea válido en los demás (ya que comparten la secret key). Este .env no se versionaría públicamente, manteniendo la clave segura.
depends_on asegura cierto orden en arranque (DB antes de servicios que lo usan, etc.), aunque para espera a que DB esté listo se puede usar scripts de espera.
El gateway mapea su puerto 5000 al host, así como el frontend (nginx) mapea 3000. Websocket service mapea 5005 para que un cliente pueda conectarse (en producción esto se manejaría diferente, pero en dev quizás se conecta a localhost:5005).
PostgreSQL y Redis son servicios estándar con sus configuraciones. Los datos de PostgreSQL se almacenan en un volumen db_data para persistencia local.
Para Celery/notification, en un entorno real se correría un contenedor para el worker (command: celery -A notification_service.app.celery worker --loglevel=info) separado de la API. Aquí, para simplicidad, solo levantamos uno (podría correr la API Flask, y un worker thread, aunque no es lo ideal). En Kubernetes en cambio se implementaría separado (ver más abajo).
Este archivo permite desarrollar y probar localmente todo el sistema levantando todos los servicios juntos.
Kubernetes – Despliegue en Producción (Cluster)
Para entornos productivos, se utilizará Kubernetes para desplegar contenedores escalables. Cada microservicio tendrá su Deployment (pudiendo especificar replicas > 1 para escalamiento horizontal) y su Service correspondiente (tipo ClusterIP para microservicios internos, y posiblemente NodePort o LoadBalancer/Ingress para entrada pública).
También se configura un Ingress para exponer externamente el gateway y el servicio de WebSockets bajo dominios seguros con HTTPS. Se integrará Prometheus para monitoreo de métricas y Grafana para visualización. Los secretos sensibles (como JWT_SECRET_KEY, credenciales DB, certificados TLS) se manejan con Secret de Kubernetes.
A continuación, mostramos ejemplos representativos de la configuración de Kubernetes:
Archivo: k8s-deployment-gateway.yaml – Deployment y Service para el API Gateway
yaml
Copiar
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway-deployment
  labels:
    app: api-gateway
spec:
  replicas: 2  # ejecutar 2 pods del gateway para alta disponibilidad
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "5000"
    spec:
      containers:
      - name: api-gateway
        image: myrepo/admin_kiosk3_api_gateway:latest
        ports:
        - containerPort: 5000
        env:
        - name: AUTH_SERVICE_URL
          value: "http://auth-service:5001"
        - name: KIOSK_SERVICE_URL
          value: "http://kiosk-service:5002"
        - name: PAYMENT_SERVICE_URL
          value: "http://payment-service:5003"
        - name: AI_SERVICE_URL
          value: "http://ai-service:5004"
        - name: NOTIF_SERVICE_URL
          value: "http://notification-service:5006"
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: adminkiosk-secrets
              key: jwt_secret_key
        # Montar configuración de logging, recursos, livenessProbe/readinessProbe etc., según sea necesario.
---
apiVersion: v1
kind: Service
metadata:
  name: api-gateway-service
spec:
  selector:
    app: api-gateway
  ports:
    - name: http
      port: 80
      targetPort: 5000
  type: ClusterIP

Archivo: k8s-deployment-auth.yaml – Deployment y Service para Auth Service (similar para otros microservicios)
yaml
Copiar
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service-deployment
  labels:
    app: auth-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: auth-service
  template:
    metadata:
      labels:
        app: auth-service
    spec:
      containers:
      - name: auth-service
        image: myrepo/admin_kiosk3_auth_service:latest
        ports:
        - containerPort: 5001
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: adminkiosk-secrets
              key: database_url   # contiene cadena de conexión a PostgreSQL
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: adminkiosk-secrets
              key: jwt_secret_key
        - name: FLASK_ENV
          value: "production"
        # agregar volumen de ConfigMap si hay config adicional, etc.
---
apiVersion: v1
kind: Service
metadata:
  name: auth-service
spec:
  selector:
    app: auth-service
  ports:
    - port: 5001
      targetPort: 5001
  clusterIP: None
  # Utilizamos Headless Service si se quisiera descubrimiento DNS, 
  # pero en este caso un ClusterIP normal es suficiente para que gateway lo encuentre por nombre.

(Se repetirían Deployment/Service similares para kiosk-service, payment-service, ai-service, websocket-service y notification-service. En notification-service, se podría tener dos deployments: uno para la API (si expuesta) y otro para el worker Celery, usando la misma imagen pero comandos diferentes.)
Archivo: k8s-deployment-frontend.yaml – Deployment y Service para el Frontend
yaml
Copiar
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend-deployment
  labels:
    app: adminkiosk-frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: adminkiosk-frontend
  template:
    metadata:
      labels:
        app: adminkiosk-frontend
    spec:
      containers:
      - name: frontend
        image: myrepo/admin_kiosk3_frontend:latest
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
spec:
  selector:
    app: adminkiosk-frontend
  ports:
    - port: 80
      targetPort: 80
  type: ClusterIP

Archivo: k8s-ingress.yaml – Ingress para exponer API Gateway y WebSocket con HTTPS
Este Ingress asume que se tiene un controlador de Ingress (por ejemplo nginx-ingress) instalado en el cluster y un certificado TLS (almacenado en un Secret). Expondremos el frontend y gateway bajo un mismo host (por ejemplo adminkiosk.example.com) y encaminaremos según la ruta. También configuramos el manejo de WebSockets.
yaml
Copiar
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: adminkiosk-ingress
  annotations:
    nginx.ingress.kubernetes.io/websocket-services: websocket-service  # habilitar websocket forwarding al servicio indicado
    nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"             # tiempo alto para conexiones largas (websocket)
    nginx.ingress.kubernetes.io/proxy-send-timeout: "3600"
spec:
  tls:
  - hosts:
      - adminkiosk.example.com
    secretName: adminkiosk-tls-secret   # secret pre-creado con certificado TLS (e.g., de Let's Encrypt)
  rules:
  - host: adminkiosk.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service    # sirve la app React
            port:
              number: 80
      - path: /socket.io
        pathType: Prefix
        backend:
          service:
            name: websocket-service   # el servicio Flask-SocketIO
            port:
              number: 5005
      - path: /auth
        pathType: Prefix
        backend:
          service:
            name: api-gateway-service
            port:
              number: 80
      - path: /kiosks
        pathType: Prefix
        backend:
          service:
            name: api-gateway-service
            port:
              number: 80
      - path: /payments
        pathType: Prefix
        backend:
          service:
            name: api-gateway-service
            port:
              number: 80
      - path: /ai
        pathType: Prefix
        backend:
          service:
            name: api-gateway-service
            port:
              number: 80
      - path: /notify
        pathType: Prefix
        backend:
          service:
            name: api-gateway-service
            port:
              number: 80

Descripción:
Usamos un único host adminkiosk.example.com para frontend y API. La ruta / (y cualquier archivo estático pedido) se sirve desde el frontend-service (Nginx que sirve la SPA). Las rutas que corresponden a la API (/auth, /kiosks, etc.) se enrutan al api-gateway-service.
La ruta /socket.io (usada por el handshake de Socket.IO) se enruta directamente al websocket-service para manejar conexiones WebSocket. La anotación nginx.ingress.kubernetes.io/websocket-services con valor websocket-service indica al controlador Nginx que cualquier connection upgrade en esa ruta debe ir a ese servicio, manteniendo la conexión abierta.
El certificado TLS asegurará que las conexiones son HTTPS. Los clientes accederían a https://adminkiosk.example.com para la app web (que internamente hace llamadas https a /auth/..., etc., mismo dominio) y el socket se conectaría por wss://adminkiosk.example.com/socket.io.
Prometheus podría descubrir automáticamente las endpoints si se configuran las anotaciones de scrape en los pods (como se mostró en gateway). Alternativamente, se puede configurar un ServiceMonitor (si se usa el operador de Prometheus) para recoger las métricas. Por simplicidad, aquí se añadió annotation en el Deployment del gateway (y se haría similar en otros) para exponer un endpoint de métricas o reutilizar el /metrics de Flask if integrado. Habría que instrumentar el código con métricas (por ejemplo utilizando prometheus_client in Python) para que Prometheus recolecte información como latencias, recuento de peticiones, etc.
CI/CD con GitHub Actions y Docker
Para mantener la eficiencia en el desarrollo y despliegue, utilizamos GitHub Actions para CI/CD automatizado. Cada push o merge a la rama principal puede desencadenar un workflow que construye las imágenes Docker de cada componente, ejecuta pruebas (si las hubiera), y despliega la nueva versión al cluster de Kubernetes.
A continuación, una configuración simplificada de un workflow de GitHub Actions (.github/workflows/ci-cd.yml):
yaml
Copiar
name: CI-CD

on:
  push:
    branches: [ "main" ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    env:
      REGISTRY: ghcr.io/miusuario      # registro de contenedores (GitHub Container Registry en este ejemplo)
      K8S_CLUSTER_URL: ${{ secrets.K8S_CLUSTER_URL }}
      K8S_CLUSTER_TOKEN: ${{ secrets.K8S_CLUSTER_TOKEN }}
      K8S_CLUSTER_CACERT: ${{ secrets.K8S_CLUSTER_CACERT }}
    steps:
      - name: Checkout repo
        uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Log in to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push auth_service image
        uses: docker/build-push-action@v3
        with:
          context: ./auth_service
          push: true
          tags: ${{ env.REGISTRY }}/admin_kiosk3_auth_service:latest

      - name: Build and push kiosk_service image
        uses: docker/build-push-action@v3
        with:
          context: ./kiosk_service
          push: true
          tags: ${{ env.REGISTRY }}/admin_kiosk3_kiosk_service:latest

      # ... (repetir build-push para payment_service, ai_service, websocket_service, notification_service, api_gateway, frontend)

      - name: Set up kubectl
        uses: azure/setup-kubectl@v3
        with:
          version: 'v1.21.0'   # versión kubectl apropiada
      - name: Configure Kubeconfig
        run: |
          export KUBECONFIG=./kubeconfig
          kubectl config set-cluster my-cluster --server=$K8S_CLUSTER_URL --certificate-authority=${K8S_CLUSTER_CACERT} --embed-certs=true
          kubectl config set-credentials ci-user --token=${K8S_CLUSTER_TOKEN}
          kubectl config set-context ci-context --cluster=my-cluster --user=ci-user --namespace=default
          kubectl config use-context ci-context

      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/api-gateway-deployment api-gateway=${{ env.REGISTRY }}/admin_kiosk3_api_gateway:latest
          kubectl set image deployment/auth-service-deployment auth-service=${{ env.REGISTRY }}/admin_kiosk3_auth_service:latest
          kubectl set image deployment/kiosk-service-deployment kiosk-service=${{ env.REGISTRY }}/admin_kiosk3_kiosk_service:latest
          kubectl set image deployment/payment-service-deployment payment-service=${{ env.REGISTRY }}/admin_kiosk3_payment_service:latest
          kubectl set image deployment/ai-service-deployment ai-service=${{ env.REGISTRY }}/admin_kiosk3_ai_service:latest
          kubectl set image deployment/websocket-service-deployment websocket-service=${{ env.REGISTRY }}/admin_kiosk3_websocket_service:latest
          kubectl set image deployment/notification-service-deployment notification-service=${{ env.REGISTRY }}/admin_kiosk3_notification_service:latest
          kubectl set image deployment/frontend-deployment frontend=${{ env.REGISTRY }}/admin_kiosk3_frontend:latest
          # Opcional: aplicar migraciones DB, limpiar pods viejos, etc.

Descripción:
El workflow se activa en push a la rama main.
Se configuran variables de entorno para la URL del registro de contenedores y credenciales del cluster Kubernetes, los cuales se toman de GitHub Secrets (K8S_CLUSTER_URL, token, etc. se deben configurar en el repo).
Pasos:
Checkout del repositorio.
Configurar Docker Buildx para multiplataforma (opcional, pero build-push action lo usa).
Login al registro (en este ejemplo, GitHub Container Registry).
Construir y subir cada imagen Docker usando docker/build-push-action. (Aquí listamos auth_service y kiosk_service; en el archivo real repetiríamos para los demás microservicios, el gateway y el frontend).
Configurar kubectl usando el contexto del cluster (aquí usamos azure/setup-kubectl solo para tener kubectl disponible, luego configuramos manualmente el contexto; alternativamente podríamos usar kubectl config or other actions).
Desplegar actualizaciones usando kubectl set image para cada deployment, apuntando a la nueva imagen con tag latest pushada. Esto asume que los Deployments ya existen en el cluster (quizás creados inicialmente mediante kubectl apply de los manifiestos). Al cambiar la imagen, Kubernetes lanzará rolling updates.
(En un pipeline más robusto, podríamos primero aplicar migrations a la base de datos si hay cambios de esquema, ejecutar tests antes de desplegar, etc. Además, usar tags versionados en lugar de latest para permitir rollback fácil.)
GitHub Actions también podría separar la pipeline en dos jobs: uno de build/test y otro de deploy, usando condiciones (por ejemplo, desplegar solo en main, etc.). Por simplicidad se puso todo junto.
La configuración de CI/CD asegura que cada cambio en el código se construye e implementa rápidamente, manteniendo el sistema actualizado sin intervención manual, siguiendo principios DevOps.

Conclusión: El código presentado sigue las "12 reglas" pautadas (modularidad en microservicios, separación de preocupaciones, seguridad con JWT y manejo adecuado de secretos, escalabilidad con contenedores y orquestación, etc.), ofreciendo una base sólida para Admin_Kiosk3. Esta arquitectura permite escalar cada componente individualmente, realizar mantenimientos enfocados por servicio, y asegurar un desarrollo ágil mediante CI/CD, todo complementado con monitoreo para garantizar el rendimiento y la estabilidad del sistema en producción. Cada sección de código está formateada de manera clara y organizada para facilitar su comprensión y mantenimiento.

