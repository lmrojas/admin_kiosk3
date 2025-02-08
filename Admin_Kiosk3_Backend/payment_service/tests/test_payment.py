import unittest
from flask import json
from Admin_Kiosk3_Backend.payment_service.app import app
from Admin_Kiosk3_Backend.payment_service.models import db, Payment
from decimal import Decimal

class PaymentTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        self.db = db
        
        # Crear tablas y pago de prueba
        with app.app_context():
            db.create_all()
            test_payment = Payment(
                user_id=1,
                kiosk_id=1,
                amount=Decimal('100.00'),
                status='completed'
            )
            db.session.add(test_payment)
            db.session.commit()
    
    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_get_payment(self):
        """Test obtener información de pago"""
        response = self.app.get('/payments/1')  # ID del pago de prueba
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'completed')

if __name__ == '__main__':
    unittest.main() 