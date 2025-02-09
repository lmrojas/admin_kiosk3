from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from Admin_Kiosk3_Backend.common.utils import format_timestamp
from Admin_Kiosk3_Backend.common import db

class Notification(db.Model):
    """Modelo para notificaciones"""
    __tablename__ = 'notifications'
    __table_args__ = {'schema': 'notify'}  # Especificar esquema
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_at = db.Column(db.DateTime)
    
    # Referencias con esquemas
    user_id = db.Column(db.Integer, db.ForeignKey('auth.users.id'), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'message': self.message,
            'status': self.status,
            'created_at': format_timestamp(self.created_at),
            'sent_at': format_timestamp(self.sent_at)
        } 