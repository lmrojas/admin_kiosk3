from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from Admin_Kiosk3_Backend.common.utils import format_timestamp
from Admin_Kiosk3_Backend.common import db

class WebSocketConnection(db.Model):
    """Modelo para conexiones WebSocket"""
    __tablename__ = 'connections'
    __table_args__ = {'schema': 'ws'}  # Especificar esquema
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(20), default='active')
    connected_at = db.Column(db.DateTime, default=datetime.utcnow)
    disconnected_at = db.Column(db.DateTime)
    
    # Referencias con esquemas
    user_id = db.Column(db.Integer, db.ForeignKey('auth.users.id'), nullable=False)
    kiosk_id = db.Column(db.Integer, db.ForeignKey('kiosk.kiosks.id'), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'connected_at': format_timestamp(self.connected_at),
            'disconnected_at': format_timestamp(self.disconnected_at),
            'status': self.status
        } 