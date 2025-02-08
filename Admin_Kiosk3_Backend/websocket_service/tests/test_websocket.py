import unittest
from flask import json
from Admin_Kiosk3_Backend.websocket_service.app import app, socketio
from flask_socketio import SocketIOTestClient

class WebSocketTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.socket_client = SocketIOTestClient(app, socketio)
    
    def tearDown(self):
        self.socket_client.disconnect()
    
    def test_connect(self):
        """Test de conexión WebSocket"""
        self.socket_client.connect()
        received = self.socket_client.get_received()
        self.assertTrue(len(received) > 0)
        self.assertEqual(received[0]['name'], 'connection_response')
    
    def test_broadcast(self):
        """Test de broadcast de mensaje"""
        self.socket_client.connect()
        response = self.app.post('/broadcast',
            json={'message': 'test message'})
        self.assertEqual(response.status_code, 200)
        received = self.socket_client.get_received()
        self.assertTrue(any(msg['name'] == 'broadcast_message' for msg in received))

if __name__ == '__main__':
    unittest.main() 