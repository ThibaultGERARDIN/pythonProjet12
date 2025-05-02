from .database_controller import SessionLocal
from models.contracts import Contract
from datetime import datetime


def create_contract(client_id, sales_contact_id, amount_total, amount_remaining, is_signed):
    db = SessionLocal()
    try:
        contract = Contract(
            client_id=client_id,
            sales_contact_id=sales_contact_id,
            amount_total=amount_total,
            amount_remaining=amount_remaining,
            is_signed=is_signed,
            created_at=datetime.now(),
        )
        db.add(contract)
        db.commit()
        return True, f"Contrat créé pour client #{client_id}."
    finally:
        db.close()


def list_contracts():
    db = SessionLocal()
    try:
        return db.query(Contract).all()
    finally:
        db.close()


def update_contract(contract_id, **kwargs):
    db = SessionLocal()
    try:
        contract = db.query(Contract).filter_by(id=contract_id).first()
        if not contract:
            return False, "Contrat non trouvé."
        for key, value in kwargs.items():
            if value is not None:
                setattr(contract, key, value)
        db.commit()
        return True, f"Contrat #{contract_id} mis à jour."
    finally:
        db.close()


def delete_contract(contract_id):
    db = SessionLocal()
    try:
        contract = db.query(Contract).filter_by(id=contract_id).first()
        if not contract:
            return False, "Contrat non trouvé."
        db.delete(contract)
        db.commit()
        return True, f"Contrat #{contract_id} supprimé."
    finally:
        db.close()
