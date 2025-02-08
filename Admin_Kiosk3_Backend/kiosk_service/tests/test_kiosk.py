import unittest
from flask import json
from Admin_Kiosk3_Backend.kiosk_service.app import app
from Admin_Kiosk3_Backend.kiosk_service.models import db, Kiosk

class KioskTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        self.db = db
        
        # Crear tablas y kiosko de prueba
        with app.app_context():
            db.create_all()
            test_kiosk = Kiosk(code='TEST001', name='Test Kiosk', location='Test Location')
            db.session.add(test_kiosk)
            db.session.commit()
    
    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_get_kiosk(self):
        """Test obtener información de kiosko"""
        response = self.app.get('/kiosks/1')  # ID del kiosko de prueba
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 'TEST001')

if __name__ == '__main__':
    unittest.main() 