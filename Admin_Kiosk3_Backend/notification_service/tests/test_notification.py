import unittest
from flask import json
from Admin_Kiosk3_Backend.notification_service.app import app
from Admin_Kiosk3_Backend.notification_service.models import db, Notification
import datetime

class NotificationTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        self.db = db
        
        # Crear tablas y notificación de prueba
        with app.app_context():
            db.create_all()
            test_notification = Notification(
                user_id=1,
                type='email',
                content='Test notification content',
                status='pending'
            )
            db.session.add(test_notification)
            db.session.commit()
    
    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_send_notification(self):
        """Test de envío de notificación"""
        response = self.app.post('/notify/email',
            json={
                'to': 'test@example.com',
                'subject': 'Test Subject',
                'body': 'Test Body'
            })
        self.assertEqual(response.status_code, 202)
        data = json.loads(response.data)
        self.assertIn('message', data)

if __name__ == '__main__':
    unittest.main() 