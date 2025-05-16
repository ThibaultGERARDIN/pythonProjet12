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
    Manage the access to ``User`` table.
    """

    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=User)

    @permission_required(roles=Department)
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    @permission_required(roles=[Department.ACCOUNTING])
    def get_all(self):
        return super().get_all()

    def _create_admin_raw(self, firstname, lastname, email, password):
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
        return super().delete(where_clause)

    def resolve_cascade(self, users: List[User]) -> List[CascadeDetails]:
        return self.cascade_resolver.resolve_user_cascade(users=users)
