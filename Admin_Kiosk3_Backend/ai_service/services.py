from Admin_Kiosk3_Backend.ai_service.models import AIModel, db
from Admin_Kiosk3_Backend.common.logging.logger import get_logger
import joblib
import os
import numpy as np
from datetime import datetime

log = get_logger('ai_service')

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'model.pkl')

def load_model():
    """Cargar modelo entrenado desde archivo"""
    try:
        from Admin_Kiosk3_Backend.ai_service.config import Config
        model = joblib.load(Config.MODEL_PATH)
        log.info("Modelo cargado exitosamente")
        return model
    except Exception as e:
        log.error(f"Error cargando modelo: {str(e)}")
        return None

def make_prediction(features, model):
    """Realizar predicción usando el modelo"""
    try:
        features_array = np.array(features).reshape(1, -1)
        prediction = model.predict(features_array)[0]
        log.info(f"Predicción realizada: {prediction}")
        return prediction
    except Exception as e:
        log.error(f"Error en predicción: {str(e)}")
        raise Exception(f"Error en predicción: {str(e)}")

def update_model_metrics(model_id: int, metrics: dict):
    """Actualizar métricas del modelo"""
    model = AIModel.query.get(model_id)
    if model:
        model.metrics = metrics
        model.updated_at = datetime.utcnow()
        db.session.commit()
        log.info(f"Métricas actualizadas para modelo {model_id}")
        return True
    return False