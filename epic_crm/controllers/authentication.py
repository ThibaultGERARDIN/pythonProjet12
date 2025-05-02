import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from models.users import User
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy.orm import Session


load_dotenv()


def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())


SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_current_user_token_payload():
    """
    Payload returned :
    {"user_id": user.id, "email": user.email, "role": user.role}
    """
    try:
        with open(".token", "r") as f:
            token = f.read().strip()
        payload = decode_token(token)
        if not payload:
            raise ValueError("Token invalide ou expiré.")
        return payload
    except FileNotFoundError:
        raise ValueError("Token non trouvé. Veuillez vous connecter.")


def retrieve_authenticated_user(session: Session) -> User:
    user_id = get_current_user_token_payload()["user_id"]

    return session.scalar(sqlalchemy.select(User).where(User.id == user_id))
