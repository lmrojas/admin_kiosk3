import unittest
from flask import json
from Admin_Kiosk3_Backend.auth_service.app import app
from Admin_Kiosk3_Backend.auth_service.models import db, User
from Admin_Kiosk3_Backend.common.config import Config

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        self.db = db
        
        # Crear tablas y usuario de prueba
        with app.app_context():
            db.create_all()
            test_user = User(username='test_user', email='test@test.com')
            test_user.set_password('test_password')
            test_user.role = 'user'
            db.session.add(test_user)
            db.session.commit()
    
    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_login(self):
        """Test de login exitoso"""
        response = self.app.post('/auth/login',
            json={'username': 'test_user', 'password': 'test_password'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('token', data)
        self.assertEqual(data['user']['username'], 'test_user')

    def test_register(self):
        """Test de registro de usuario"""
        response = self.app.post('/auth/register',
            json={
                'username': 'new_user',
                'password': 'new_password',
                'email': 'new@test.com'
            })
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('new_user', data['message'])

if __name__ == '__main__':
    unittest.main() 