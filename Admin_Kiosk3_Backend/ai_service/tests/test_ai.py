import unittest
from flask import json
from Admin_Kiosk3_Backend.ai_service.app import app
from Admin_Kiosk3_Backend.ai_service.models import db, AIModel
import numpy as np

class AITestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        self.db = db
        
        # Crear tablas y modelo de prueba
        with app.app_context():
            db.create_all()
            test_model = AIModel(
                name='test_model',
                version='1.0',
                status='active',
                metrics={'accuracy': 0.95}
            )
            db.session.add(test_model)
            db.session.commit()
    
    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_predict(self):
        """Test de predicción del modelo"""
        test_features = np.random.rand(5).tolist()  # 5 features aleatorias
        response = self.app.post('/ai/predict',
            json={'features': test_features})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('prediction', data)

if __name__ == '__main__':
    unittest.main() 