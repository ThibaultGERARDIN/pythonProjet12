from sqlalchemy.orm import Session
from typing import List

from controllers.authentication import get_current_user_token_payload
from models.users import User, Department
from controllers.database_controller import SessionLocal


def resolve_permission(roles: List[Department], function, *args, **kwargs):
    """
    Execute a function if the currently authenticated user has a role included in the allowed list.

    This function fetches the user from the database using their JWT payload and verifies
    their role against the allowed `roles`. If the check passes, the target function is called.

    Args:
        roles (List[Department]): List of authorized departments.
        function (Callable): The function to execute if permission is granted.
        *args: Positional arguments to pass to the target function.
        **kwargs: Keyword arguments to pass to the target function.

    Returns:
        Any: The result of the function call if permission is granted.

    Raises:
        PermissionError: If the user is not found or their role is not in the allowed list.
    """
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
    Decorator that restricts function execution to users with specific roles.

    This decorator checks if the currently authenticated user's role is among
    the allowed `roles`. If not, a `PermissionError` is raised.

    Example:
        @permission_required([Department.SALES])
        def some_function():
            ...

    Args:
        roles (List[Department]): A list of `Department` enums authorized to call the function.

    Returns:
        Callable: Wrapped function with access control.

    Raises:
        PermissionError: If the user is not authorized.
    """

    def decorator(function):
        def wrapper(*args, **kwargs):
            return resolve_permission(roles, function, *args, **kwargs)

        return wrapper

    return decorator
