import bcrypt
import jwt
import os
import click
from datetime import datetime, timedelta
from models.users import User
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy.orm import Session
from .database_controller import SessionLocal


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
MASTER_PASSWORD = os.getenv("MASTER_PASSWORD")


def hash_password(password):
    """
    Hash a plaintext password using bcrypt.

    Args:
        password (str): The plaintext password.

    Returns:
        str: The hashed password.
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password, hashed):
    """
    Verify a plaintext password against a hashed version.

    Args:
        password (str): The plaintext password to verify.
        hashed (str): The hashed password to compare with.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return bcrypt.checkpw(password.encode(), hashed.encode())


def require_master_password(function):
    """
    Decorator that prompts for the master password before allowing access
    to a CLI command. Aborts if the password is incorrect.

    Args:
        function (Callable): The CLI command to wrap.

    Returns:
        Callable: The wrapped function.
    """

    def wrapper(*args, **kwargs):
        pwd = click.prompt("Mot de passe administrateur", hide_input=True)
        if pwd != MASTER_PASSWORD:
            click.secho("Mot de passe incorrect. Accès refusé.", fg="red")
            return
        return function(*args, **kwargs)

    return wrapper


def create_access_token(data: dict):
    """
    Generate a JWT access token with an expiration time.

    Args:
        data (dict): The payload data to encode into the token.

    Returns:
        str: The JWT token as a string.
    """
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    """
    Decode a JWT token and return its payload.

    Args:
        token (str): The JWT token to decode.

    Returns:
        dict or None: The decoded payload, or None if invalid or expired.
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def authenticate_user(email, password):
    """
    Authenticate a user by email and password.

    Args:
        email (str): The user's email.
        password (str): The user's plaintext password.

    Returns:
        Tuple[bool, str]:
            - If successful: (True, JWT token)
            - If failed: (False, error message)
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(email=email).first()
        if user and verify_password(password, user.hashed_password):
            token = create_access_token({"user_id": user.id, "role": user.role.name})
            return True, token
        else:
            return False, "Email ou mot de passe incorrect."
    finally:
        db.close()


def get_current_user_token_payload():
    """
    Retrieve the JWT payload of the currently logged-in user.

    The payload contains:
        {
            "user_id": <int>,
            "role": <str>,
            "exp": <timestamp>
        }

    Returns:
        dict: The decoded payload from the .token file.

    Raises:
        ValueError: If token file is missing, invalid, or expired.
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
    """
    Get the currently authenticated user from the database using the token payload.

    Args:
        session (Session): SQLAlchemy session.

    Returns:
        User: The user object from the database.
    """
    user_id = get_current_user_token_payload()["user_id"]

    return session.scalar(sqlalchemy.select(User).where(User.id == user_id))
