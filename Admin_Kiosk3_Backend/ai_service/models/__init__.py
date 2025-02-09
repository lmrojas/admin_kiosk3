# Archivo vacío para marcar el directorio como paquete Python 

from Admin_Kiosk3_Backend import db
from datetime import datetime
from Admin_Kiosk3_Backend.common.utils import format_timestamp

class AIModel(db.Model):
    __tablename__ = 'ai_models'
    __table_args__ = {'schema': 'ai'}  # Especificar esquema
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    version = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), default='active')
    accuracy = db.Column(db.Float)
    parameters = db.Column(db.JSON, default={})
    training_data = db.Column(db.JSON, default={})
    
    def to_dict(self):
        """Convertir el modelo a diccionario según reglas MDC"""
        return {
            'id': self.id,
            'name': self.name,
            'version': self.version,
            'status': self.status,
            'accuracy': self.accuracy,
            'created_at': format_timestamp(self.created_at),
            'updated_at': format_timestamp(self.updated_at)
        }
    
    def __repr__(self):
        return f'<AIModel {self.name} v{self.version}>' 