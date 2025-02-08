import logging
import sys
import json
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from Admin_Kiosk3_Backend.common.config import Config

# Configurar logger para Admin_Kiosk3_Backend
logger = logging.getLogger('Admin_Kiosk3_Backend')
logger.setLevel(logging.INFO)

# Handler para stdout
handler = logging.StreamHandler(sys.stdout)

# Formato JSON para logs estructurados
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'service': 'Admin_Kiosk3_Backend.' + record.module
        }
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id
        return json.dumps(log_record)

handler.setFormatter(JsonFormatter())
logger.addHandler(handler)

def get_logger(name=None):
    """Obtener logger configurado"""
    return logger.getChild(name) if name else logger

def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler para stdout
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)
    
    return logger 