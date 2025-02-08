from Admin_Kiosk3_Backend.payment_service.models import Payment, db
from Admin_Kiosk3_Backend.common.logging.logger import get_logger
from decimal import Decimal

log = get_logger('payment_service')

def create_payment_record(user_id: int, kiosk_id: int, amount: Decimal) -> Payment:
    """Crear un nuevo registro de pago"""
    payment = Payment(user_id=user_id, kiosk_id=kiosk_id, amount=amount)
    db.session.add(payment)
    db.session.commit()
    log.info(f"Pago creado: {payment.id}")
    return payment

def get_user_payments(user_id: int) -> list:
    """Obtener todos los pagos de un usuario"""
    return Payment.query.filter_by(user_id=user_id).all() 