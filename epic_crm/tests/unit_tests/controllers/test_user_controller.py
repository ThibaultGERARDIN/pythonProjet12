from controllers.user_controller import UserManager
from models.users import Department, User
from unittest.mock import patch


def test_user_creation(dummy_session):
    manager = UserManager(dummy_session)
    user = manager._create_admin_raw("John", "Doe", "john@doe.com", "password")
    assert user.email == "john@doe.com"
    assert user in dummy_session.data


def test_user_get_all(dummy_session, mock_auth_accounting):
    user = User(
        first_name="Jane", last_name="Doe", email="jane@doe.com", hashed_password="hash", role=Department.ACCOUNTING
    )
    dummy_session.data = [user]
    manager = UserManager(dummy_session)
    users = manager.get_all()
    assert user in users


def test_user_get_with_clause(dummy_session, mock_auth_accounting):
    user = User(
        id=1, first_name="Max", last_name="Payne", email="max@payne.com", hashed_password="pwd", role=Department.SUPPORT
    )
    dummy_session.data = [user]
    manager = UserManager(dummy_session)
    results = manager.get(User.id == 1)
    assert results == [user]


@patch(
    "controllers.user_controller.get_current_user_token_payload",
    return_value={"user_id": 1, "email": "acc@test.com", "role": "ACCOUNTING"},
)
@patch(
    "controllers.permissions.get_current_user_token_payload",
    return_value={"user_id": 1, "email": "acc@test.com", "role": "ACCOUNTING"},
)
@patch("controllers.user_controller.capture_message")  # pour éviter les erreurs de Sentry
def test_user_update(_, __, ___, dummy_session):
    dummy_session.data = [
        User(
            id=1,
            first_name="John",
            last_name="Doe",
            email="john@doe.com",
            hashed_password="pwd",
            role=Department.ACCOUNTING,
        )
    ]

    manager = UserManager(dummy_session)
    manager.update(User.id == 1, email="new@mail.com")
    assert len(dummy_session.updated) == 1


def test_user_delete(dummy_session, mock_auth_accounting):
    manager = UserManager(dummy_session)
    manager.delete(User.id == 1)
    assert len(dummy_session.updated) == 1
