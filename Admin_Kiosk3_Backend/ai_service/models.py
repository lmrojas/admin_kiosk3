from flask_sqlalchemy import SQLAlchemy
from Admin_Kiosk3_Backend.common.utils import format_timestamp
import datetime
import json

db = SQLAlchemy()

class AIModel(db.Model):
    __tablename__ = 'ai_models'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    version = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='active')  # active, training, failed
    metrics = db.Column(db.JSON)  # métricas del modelo (accuracy, precision, etc.)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'version': self.version,
            'status': self.status,
            'metrics': json.loads(self.metrics) if isinstance(self.metrics, str) else self.metrics,
            'created_at': format_timestamp(self.created_at),
            'updated_at': format_timestamp(self.updated_at)
        } 