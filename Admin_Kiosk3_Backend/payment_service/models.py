from flask_sqlalchemy import SQLAlchemy
from Admin_Kiosk3_Backend.common.utils import format_timestamp
import datetime

db = SQLAlchemy()

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)      # ID del usuario que realizó el pago
    kiosk_id = db.Column(db.Integer, nullable=False)     # ID del kiosko donde se realizó
    amount = db.Column(db.Numeric(10,2), nullable=False) # Monto del pago
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    status = db.Column(db.String(20), default='completed')  # estado del pago (completed, pending, etc.)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'kiosk_id': self.kiosk_id,
            'amount': str(self.amount),
            'timestamp': format_timestamp(self.timestamp),
            'status': self.status
        } 