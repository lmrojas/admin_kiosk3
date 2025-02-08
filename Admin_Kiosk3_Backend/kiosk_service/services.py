from .models import Kiosk, db
import uuid

def create_kiosk(name, location, code=None):
    """Crear un nuevo kiosko"""
    kiosk_code = code or str(uuid.uuid4())
    kiosk = Kiosk(code=kiosk_code, name=name, location=location)
    db.session.add(kiosk)
    db.session.commit()
    return kiosk

def assign_kiosk_to_user(kiosk_code, user_id):
    """Asignar un kiosko a un usuario"""
    kiosk = Kiosk.query.filter_by(code=kiosk_code).first()
    if kiosk:
        kiosk.assigned_to = user_id
        db.session.commit()
        return True
    return False 