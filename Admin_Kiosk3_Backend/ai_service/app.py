import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required
import joblib
import numpy as np
from Admin_Kiosk3_Backend.common.config import Config
from Admin_Kiosk3_Backend.common.logging.logger import get_logger
from Admin_Kiosk3_Backend.ai_service.models import AIModel, db

app = Flask(__name__)
Config.init_app(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://user:password@db:5432/admin_kiosk3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'super-secret-key')
db = SQLAlchemy(app)
jwt = JWTManager(app)
log = get_logger('ai_service')

# Cargar modelo entrenado
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'model.pkl')
model = None
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)

@app.route('/ai/predict', methods=['POST'])
@jwt_required()
def predict():
    """Endpoint para obtener predicciones del modelo"""
    if not model:
        return jsonify({'message': 'Modelo no disponible'}), 503
    
    data = request.get_json()
    if not data or 'features' not in data:
        return jsonify({'message': 'Datos de entrada no proporcionados'}), 400
    
    try:
        features = np.array(data['features']).reshape(1, -1)
        prediction = model.predict(features)[0]
        return jsonify({'prediction': prediction.tolist()}), 200
    except Exception as e:
        return jsonify({'message': f'Error al procesar predicción: {str(e)}'}), 500

@app.route('/ai/metrics', methods=['GET'])
@jwt_required()
def get_metrics():
    """Obtener métricas del modelo (ejemplo: accuracy, etc.)"""
    if not model:
        return jsonify({'message': 'Modelo no disponible'}), 503
    
    metrics = {
        'model_type': type(model).__name__,
        'features_count': model.n_features_in_ if hasattr(model, 'n_features_in_') else None,
        'last_training': 'Not available'
    }
    return jsonify(metrics), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004) 