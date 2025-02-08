from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from .models import AIModel, db
from .services import load_model, make_prediction

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/predict', methods=['POST'])
@jwt_required()
def predict():
    """Endpoint para obtener predicciones del modelo"""
    model = load_model()
    if not model:
        return jsonify({'message': 'Modelo no disponible'}), 503
    
    data = request.get_json()
    if not data or 'features' not in data:
        return jsonify({'message': 'Datos de entrada no proporcionados'}), 400
    
    try:
        prediction = make_prediction(data['features'], model)
        return jsonify({'prediction': prediction.tolist()}), 200
    except Exception as e:
        return jsonify({'message': f'Error al procesar predicción: {str(e)}'}), 500

@ai_bp.route('/metrics', methods=['GET'])
@jwt_required()
def get_metrics():
    """Obtener métricas del modelo activo"""
    active_model = AIModel.query.filter_by(status='active').first()
    if not active_model:
        return jsonify({'message': 'No hay modelo activo'}), 404
    return jsonify(active_model.metrics), 200 