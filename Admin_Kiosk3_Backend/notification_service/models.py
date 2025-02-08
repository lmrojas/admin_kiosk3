from flask_sqlalchemy import SQLAlchemy
from Admin_Kiosk3_Backend.common.utils import format_timestamp
import datetime

db = SQLAlchemy()

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # email, sms, push, etc.
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, sent, failed
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    sent_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'content': self.content,
            'status': self.status,
            'created_at': format_timestamp(self.created_at),
            'sent_at': format_timestamp(self.sent_at)
        } 