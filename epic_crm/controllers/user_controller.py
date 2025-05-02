from sqlalchemy.exc import IntegrityError
from models.users import User
from .authentication import hash_password, verify_password, create_access_token
from .database_controller import SessionLocal


def create_user(firstname, lastname, email, password, role):
    db = SessionLocal()
    try:
        user = User(
            first_name=firstname, last_name=lastname, email=email, hashed_password=hash_password(password), role=role
        )
        db.add(user)
        db.commit()
        return True, f"Utilisateur '{firstname} {lastname}' créé avec succès."
    except IntegrityError:
        db.rollback()
        return False, "Un utilisateur avec cet email existe déjà."
    finally:
        db.close()


def authenticate_user(email, password):
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(email=email).first()
        if user and verify_password(password, user.hashed_password):
            token = create_access_token({"user_id": user.id, "email": user.email, "role": user.role})
            return True, token
        else:
            return False, "Email ou mot de passe incorrect."
    finally:
        db.close()
