import pytest
from sqlalchemy.orm import Session
from controllers.authentication import (
    hash_password,
    authenticate_user,
    create_access_token,
    decode_token,
    retrieve_authenticated_user,
)
from controllers import authentication
from models.users import User, Department

pytestmark = pytest.mark.usefixtures("setup_database")


@pytest.fixture
def new_user():
    return User(
        first_name="Alice",
        last_name="Test",
        email="alice@example.com",
        hashed_password=hash_password("password123"),
        role=Department.SALES,
    )


def test_user_insertion_and_authentication(test_db_session, new_user, monkeypatch):
    test_db_session.add(new_user)
    test_db_session.commit()

    success, token = authentication.authenticate_user(new_user.email, "password123")
    assert success is True
    assert isinstance(token, str)

    payload = decode_token(token)
    assert payload["user_id"] == new_user.id
    assert payload["role"] == "SALES"


def test_authenticate_user_invalid_password(test_db_session: Session, new_user):
    test_db_session.add(new_user)
    test_db_session.commit()

    success, message = authenticate_user(new_user.email, "wrong-password")
    assert success is False
    assert message == "Email ou mot de passe incorrect."


def test_authenticate_user_nonexistent_email(test_db_session: Session):
    success, message = authenticate_user("ghost@example.com", "any")
    assert success is False
    assert message == "Email ou mot de passe incorrect."


def test_retrieve_authenticated_user(test_db_session: Session, new_user, monkeypatch):
    test_db_session.add(new_user)
    test_db_session.commit()

    token = create_access_token({"user_id": new_user.id, "role": new_user.role.name})
    monkeypatch.setattr("controllers.authentication.get_current_user_token_payload", lambda: decode_token(token))

    user = retrieve_authenticated_user(test_db_session)
    assert user.email == "alice@example.com"
    assert user.role == Department.SALES
