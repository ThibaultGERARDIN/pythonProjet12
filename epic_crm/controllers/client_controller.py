from .database_controller import SessionLocal
from models.clients import Client
from models.users import User
from sqlalchemy.exc import NoResultFound
from datetime import datetime


def create_client(full_name, email, phone, company_name, sales_contact_id):
    db = SessionLocal()
    try:
        client = Client(
            full_name=full_name,
            email=email,
            phone=phone,
            company_name=company_name,
            date_created=datetime.utcnow(),
            last_contact=datetime.utcnow(),
            sales_contact_id=sales_contact_id,
        )
        db.add(client)
        db.commit()
        return True, f"Client '{full_name}' créé avec succès."
    finally:
        db.close()


def list_clients():
    db = SessionLocal()
    try:
        return db.query(Client).all()
    finally:
        db.close()


def update_client(client_id, **kwargs):
    db = SessionLocal()
    try:
        client = db.query(Client).filter_by(id=client_id).first()
        if not client:
            return False, "Client non trouvé."
        for key, value in kwargs.items():
            if value is not None:
                setattr(client, key, value)
        client.last_contact = datetime.utcnow()
        db.commit()
        return True, f"Client #{client_id} mis à jour."
    finally:
        db.close()


def delete_client(client_id):
    db = SessionLocal()
    try:
        client = db.query(Client).filter_by(id=client_id).first()
        if not client:
            return False, "Client non trouvé."
        db.delete(client)
        db.commit()
        return True, f"Client #{client_id} supprimé."
    finally:
        db.close()
