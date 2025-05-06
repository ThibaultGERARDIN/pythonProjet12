import re
from models.users import User, Department
from controllers.database_controller import SessionLocal


def validate_email(email: str):
    """
    Validates an email address format.

    Args:
    * ``email``: the email to validate

    Returns:
    * A string containing the given email

    Raises:
    * ``ValueError`` if the email is not valid
    """
    if not re.fullmatch(r"\w+\.?\w+@\w+\.[a-z]+", email):
        raise ValueError(f"Invalid email: {email}")

    return email


def check_user_role(user: User, expected_role: Department):
    """
    Vérifie que l'utilisateur a le rôle attendu. Sinon, lève une ValueError.
    """
    if user.role != expected_role:
        raise ValueError(f"The user must have role '{expected_role.name}'.")


def get_manager(manager_class):
    """
    Récupère le manageur nécessaire, et la session en cours.
    """
    session = SessionLocal()
    return manager_class(session), session
