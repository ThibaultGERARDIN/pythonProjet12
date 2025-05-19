import re
from models.users import User, Department
from controllers.database_controller import SessionLocal


def validate_email(email: str):
    """
    Validate the format of an email address using a basic regular expression.

    Args:
        email (str): The email address to validate.

    Returns:
        str: The validated email address.

    Raises:
        ValueError: If the email format is invalid.
    """
    if not re.fullmatch(r"\w+\.?\w+@\w+\.[a-z]+", email):
        raise ValueError(f"Invalid email: {email}")

    return email


def check_user_role(user: User, expected_role: Department):
    """
    Ensure that the given user has the expected department role.

    Args:
        user (User): The user to check.
        expected_role (Department): The expected department role.

    Raises:
        ValueError: If the user's role does not match the expected role.
    """
    if user.role != expected_role:
        raise ValueError(f"The user must have role '{expected_role.name}'.")


def get_manager(manager_class):
    """
    Instantiate a manager and return it along with a new SQLAlchemy session.

    This is typically used in CLI views to manage context.

    Args:
        manager_class (type): The class of the manager to instantiate.

    Returns:
        Tuple[BaseManager, Session]: A tuple containing the manager instance and its associated session.
    """
    session = SessionLocal()
    return manager_class(session), session
