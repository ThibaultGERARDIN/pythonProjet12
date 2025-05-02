from .database_controller import SessionLocal
from models.events import Event


def create_event(contract_id, client_id, support_contact_id, start_date, end_date, location, attendees, notes):
    db = SessionLocal()
    try:
        event = Event(
            contract_id=contract_id,
            client_id=client_id,
            support_contact_id=support_contact_id,
            start_date=start_date,
            end_date=end_date,
            location=location,
            attendees=attendees,
            notes=notes,
        )
        db.add(event)
        db.commit()
        return True, f"Événement créé pour client #{client_id}."
    finally:
        db.close()


def list_events():
    db = SessionLocal()
    try:
        return db.query(Event).all()
    finally:
        db.close()


def update_event(event_id, **kwargs):
    db = SessionLocal()
    try:
        event = db.query(Event).filter_by(id=event_id).first()
        if not event:
            return False, "Événement non trouvé."
        for key, value in kwargs.items():
            if value is not None:
                setattr(event, key, value)
        db.commit()
        return True, f"Événement #{event_id} mis à jour."
    finally:
        db.close()


def delete_event(event_id):
    db = SessionLocal()
    try:
        event = db.query(Event).filter_by(id=event_id).first()
        if not event:
            return False, "Événement non trouvé."
        db.delete(event)
        db.commit()
        return True, f"Événement #{event_id} supprimé."
    finally:
        db.close()
