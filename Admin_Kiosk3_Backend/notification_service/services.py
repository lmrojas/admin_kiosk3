from celery import Celery
from Admin_Kiosk3_Backend.notification_service.models import Notification, db
from Admin_Kiosk3_Backend.common.logging.logger import get_logger
import datetime

log = get_logger('notification_service')
celery = Celery('notification_service', broker='redis://redis:6379/0')

@celery.task
def send_notification(notification_id):
    """Tarea Celery para enviar notificación"""
    notification = Notification.query.get(notification_id)
    if not notification:
        log.error(f"Notificación no encontrada: {notification_id}")
        return False
    
    try:
        # Aquí iría la lógica real de envío según el tipo
        # (email -> SMTP, SMS -> API de proveedor, etc.)
        log.info(f"Enviando notificación {notification.id}: {notification.content}")
        
        notification.status = 'sent'
        notification.sent_at = datetime.datetime.utcnow()
        db.session.commit()
        return True
    except Exception as e:
        notification.status = 'failed'
        db.session.commit()
        log.error(f"Error enviando notificación: {str(e)}")
        return False 