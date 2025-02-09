"""
Módulo de seguridad común para Admin Kiosk 3
"""
import os
from cryptography.fernet import Fernet

def get_encryption_key():
    """Obtener clave de encriptación desde variables de entorno"""
    key = os.getenv('ENCRYPTION_KEY')
    if not key:
        raise ValueError("ENCRYPTION_KEY no está configurada")
    return key.encode()

def encrypt_sensitive_data(data: str) -> str:
    """
    Encripta datos sensibles usando Fernet (implementación de AES)
    
    Args:
        data: String a encriptar
        
    Returns:
        String encriptado en formato base64
    """
    if not data:
        return data
        
    key = get_encryption_key()
    f = Fernet(key)
    return f.encrypt(data.encode()).decode()

def decrypt_sensitive_data(encrypted_data: str) -> str:
    """
    Desencripta datos usando la misma clave
    
    Args:
        encrypted_data: String encriptado en base64
        
    Returns:
        String original desencriptado
    """
    if not encrypted_data:
        return encrypted_data
        
    key = get_encryption_key()
    f = Fernet(key)
    return f.decrypt(encrypted_data.encode()).decode()

# Archivo vacío para marcar el directorio como paquete Python 