from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from Admin_Kiosk3_Backend.common.utils import format_timestamp
from Admin_Kiosk3_Backend.common import db

class Payment(db.Model):
    """Modelo para pagos"""
    __tablename__ = 'payments'
    __table_args__ = {'schema': 'payment'}  # Especificar esquema
    
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    payment_method = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Referencias con esquemas
    kiosk_id = db.Column(db.Integer, db.ForeignKey('kiosk.kiosks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('auth.users.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'kiosk_id': self.kiosk_id,
            'amount': str(self.amount),
            'timestamp': format_timestamp(self.created_at),
            'status': self.status
        } 