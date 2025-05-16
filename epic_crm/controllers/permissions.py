from sqlalchemy.orm import Session
from typing import List

from controllers.authentication import get_current_user_token_payload
from models.users import User, Department
from controllers.database_controller import SessionLocal


def resolve_permission(roles: List[Department], function, *args, **kwargs):
    REJECT_MESSAGE = f"Permission denied. Please login as [{' | '.join(role.name for role in roles)}]"

    user_id = get_current_user_token_payload()["user_id"]

    session: Session = SessionLocal()
    try:
        user = session.get(User, user_id)

        if not user or user.role not in roles:
            raise PermissionError(REJECT_MESSAGE)

        return function(*args, **kwargs)

    finally:
        session.close()


def permission_required(roles: List[Department]):
    """
    decorator allowing to checks if the authenticated user belongs to a given department.

    Args:
    * ``roles``: A list of ``Departement`` objects which are authorized to access the function.

    Raises:
    * ``PermissionError``
    """

    def decorator(function):
        def wrapper(*args, **kwargs):
            return resolve_permission(roles, function, *args, **kwargs)

        return wrapper

    return decorator
