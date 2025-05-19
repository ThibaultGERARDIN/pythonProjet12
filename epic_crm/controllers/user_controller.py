import sqlalchemy
from sqlalchemy.orm import Session
from typing import List
from sentry_sdk import capture_message

from controllers.authentication import hash_password, get_current_user_token_payload
from controllers.base_controller import BaseManager
from controllers.permissions import permission_required
from controllers.cascade_controller import CascadeDetails
from controllers import utils
from models.users import Department, User


class UserManager(BaseManager):
    """
    Manage the access to the ``User`` table.

    This manager provides role-restricted access and operations such as creation, update,
    deletion, and cascading resolution of users in the system.
    """

    def __init__(self, session: Session) -> None:
        """
        Initialize the UserManager with a SQLAlchemy session.

        Args:
            session (Session): SQLAlchemy session object.
        """
        super().__init__(session=session, model=User)

    @permission_required(roles=Department)
    def get(self, *args, **kwargs):
        """
        Retrieve users matching a given condition.

        Requires the user to be authenticated in any department.

        Returns:
            List[User]: List of users matching the condition.
        """
        return super().get(*args, **kwargs)

    @permission_required(roles=[Department.ACCOUNTING])
    def get_all(self):
        """
        Retrieve all users in the database.

        Restricted to users with ACCOUNTING role.

        Returns:
            List[User]: List of all users.
        """
        return super().get_all()

    def _create_admin_raw(self, firstname, lastname, email, password):
        """
        Create an initial admin (ACCOUNTING) user without requiring authentication.

        Args:
            firstname (str): First name of the user.
            lastname (str): Last name of the user.
            email (str): Email address.
            password (str): Plaintext password to hash.

        Returns:
            User: The created admin user instance.
        """
        user = User(
            first_name=firstname,
            last_name=lastname,
            email=email,
            hashed_password=hash_password(password),
            role=Department.ACCOUNTING,
        )
        return super().create(user)

    @permission_required(roles=[Department.ACCOUNTING])
    def create(self, firstname: str, lastname: str, email: str, password: str, role: Department):
        """
        Create a new user with the given details.

        Only ACCOUNTING users are allowed to perform this operation.

        Args:
            firstname (str): First name.
            lastname (str): Last name.
            email (str): Email address.
            password (str): User password in plain text.
            role (Department): Department role to assign.

        Returns:
            User: The created user instance.
        """
        new_user = User(
            first_name=firstname,
            last_name=lastname,
            email=email,
            hashed_password=hash_password(password),
            role=role,
        )

        created_user = super().create(new_user)

        if created_user is not None:
            capture_message(
                message=f"user {get_current_user_token_payload()["user_id"]} : created user {created_user.id}",
            )

        return created_user

    @permission_required(roles=[Department.ACCOUNTING])
    def update(self, where_clause, **values):
        """
        Update user attributes based on a filter.

        If email or password is provided, it is validated or hashed respectively.
        An update audit is captured via `sentry_sdk.capture_message`.

        Args:
            where_clause: SQLAlchemy clause for filtering users.
            **values: Dictionary of fields to update.
        """

        if "email" in values:
            values["email"] = utils.validate_email(values["email"])

        if "password" in values:
            password = values.pop("password")
            values["hashed_password"] = hash_password(password)

        super().update(where_clause, **values)

        request = sqlalchemy.select(User).where(where_clause)
        updated_users = list(self._session.scalars(request))

        if updated_users is not None:
            capture_message(
                message=f"user {get_current_user_token_payload()["user_id"]}"
                f" : updated users : {[user.id for user in updated_users]}",
            )

    @permission_required(roles=[Department.ACCOUNTING])
    def delete(self, where_clause):
        """
        Delete one or more users matching the provided condition.

        Only ACCOUNTING users can perform this operation.

        Args:
            where_clause: SQLAlchemy clause to filter users for deletion.
        """
        return super().delete(where_clause)

    def resolve_cascade(self, users: List[User]) -> List[CascadeDetails]:
        """
        Resolve and return all cascade-deletable objects related to the given users.

        This includes clients, contracts, and events associated with the user(s).

        Args:
            users (List[User]): List of user instances.

        Returns:
            List[CascadeDetails]: Structured details of deletable dependencies.
        """
        return self.cascade_resolver.resolve_user_cascade(users=users)
