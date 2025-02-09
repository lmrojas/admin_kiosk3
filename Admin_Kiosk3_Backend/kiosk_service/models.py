from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from Admin_Kiosk3_Backend.common.utils import format_timestamp
from Admin_Kiosk3_Backend.common import db

class Kiosk(db.Model):
    """Modelo para los kioskos"""
    __tablename__ = 'kiosks'
    __table_args__ = {'schema': 'kiosk'}  # Especificar esquema
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(100), unique=True, nullable=False)  # Código único del kiosko
    name = db.Column(db.String(100), unique=True, nullable=False)
    location = db.Column(db.String(200))
    status = db.Column(db.String(20), default='inactive')  # active, inactive, maintenance
    
    # Campos de seguimiento
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_ping = db.Column(db.DateTime)  # Último heartbeat recibido
    
    # Configuración
    config = db.Column(db.JSON)  # Configuración específica del kiosko
    assigned_to = db.Column(db.Integer, db.ForeignKey('auth.users.id'), nullable=True)  # ID del usuario asignado
    
    def to_dict(self):
        """Convertir el modelo a diccionario"""
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'location': self.location,
            'status': self.status,
            'created_at': format_timestamp(self.created_at),
            'updated_at': format_timestamp(self.updated_at),
            'last_ping': format_timestamp(self.last_ping) if self.last_ping else None,
            'config': self.config,
            'assigned_to': self.assigned_to
        }

class KioskEvent(db.Model):
    """Modelo para eventos de kioscos"""
    __tablename__ = 'kiosk_events'
    __table_args__ = {'schema': 'kiosk'}  # Especificar esquema
    
    id = db.Column(db.Integer, primary_key=True)
    kiosk_id = db.Column(db.Integer, db.ForeignKey('kiosk.kiosks.id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'kiosk_id': self.kiosk_id,
            'event_type': self.event_type,
            'description': self.description,
            'created_at': format_timestamp(self.created_at)
        } 