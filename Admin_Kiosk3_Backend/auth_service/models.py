"""Modelos de autenticación"""
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from Admin_Kiosk3_Backend.common.utils import format_timestamp
from Admin_Kiosk3_Backend.common import db

class User(db.Model):
    """Modelo de Usuario según reglas MDC"""
    __tablename__ = 'users'
    __table_args__ = {'schema': 'auth'}
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    role = db.Column(db.String(20), nullable=False, default='operator')
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Comentamos las relaciones por ahora
    # kiosks = db.relationship('Kiosk', backref='assigned_user', lazy=True)
    # payments = db.relationship('Payment', backref='user', lazy=True)
    # notifications = db.relationship('Notification', backref='user', lazy=True)
    
    def set_password(self, password):
        """Encripta y guarda la contraseña"""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Verifica la contraseña"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Actualiza timestamp del último login"""
        self.last_login = datetime.utcnow()
        db.session.commit()

    def to_dict(self):
        """Convierte el usuario a diccionario (sin datos sensibles)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role
        }

class Role(db.Model):
    """Modelo de Roles y Permisos"""
    __tablename__ = 'roles'
    __table_args__ = {'schema': 'auth'}
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.String(200))
    permissions = db.Column(db.JSON, default={})
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'permissions': self.permissions,
            'created_at': format_timestamp(self.created_at)
        } 