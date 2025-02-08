from flask_sqlalchemy import SQLAlchemy
from Admin_Kiosk3_Backend.common.utils import format_timestamp
import datetime

db = SQLAlchemy()

class WebSocketConnection(db.Model):
    __tablename__ = 'websocket_connections'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    connected_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    disconnected_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')  # active, disconnected
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'connected_at': format_timestamp(self.connected_at),
            'disconnected_at': format_timestamp(self.disconnected_at),
            'status': self.status
        } 