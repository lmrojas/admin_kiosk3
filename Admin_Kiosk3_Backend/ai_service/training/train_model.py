import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
import os
from Admin_Kiosk3_Backend.common.logging.logger import get_logger
from Admin_Kiosk3_Backend.ai_service.config import Config

log = get_logger('ai_training')

def train_model():
    """Script de entrenamiento del modelo"""
    # En un caso real, cargaríamos datos de una fuente real
    # Por ejemplo, datos históricos de ventas de kioskos
    
    # Simulación de datos de ejemplo
    data = pd.DataFrame({
        'feature1': np.random.rand(1000),
        'feature2': np.random.rand(1000),
        'target': np.random.randint(0, 2, 1000)
    })
    
    X = data[['feature1', 'feature2']]
    y = data['target']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    
    # Guardar el modelo entrenado
    joblib.dump(model, Config.MODEL_PATH)
    
    accuracy = model.score(X_test, y_test)
    log.info(f'Modelo entrenado con accuracy: {accuracy}')
    return accuracy

if __name__ == '__main__':
    accuracy = train_model()
    print(f'Modelo entrenado con accuracy: {accuracy}') 