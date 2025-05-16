import os
import tempfile
import pytest
import jwt
from unittest.mock import patch, MagicMock

from controllers.authentication import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
    authenticate_user,
    get_current_user_token_payload,
    retrieve_authenticated_user,
    SECRET_KEY,
    ALGORITHM,
)
from models.users import User, Department


def test_hash_and_verify_password():
    password = "securePassword123"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)


def test_verify_password_invalid():
    password = "securePassword123"
    hashed = hash_password(password)
    assert not verify_password("wrongPassword", hashed)


def test_create_and_decode_token():
    data = {"user_id": 1, "role": "SALES"}
    token = create_access_token(data)
    decoded = decode_token(token)
    assert decoded["user_id"] == 1
    assert decoded["role"] == "SALES"


def test_decode_token_expired():
    expired_token = jwt.encode(
        {"user_id": 1, "exp": 0},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    assert decode_token(expired_token) is None


def test_authenticate_user_success(monkeypatch):
    fake_user = User(
        id=1,
        email="test@example.com",
        hashed_password=hash_password("password123"),
        role=Department.SALES,
        first_name="Toto",
        last_name="Tutu",
    )

    mock_session = MagicMock()
    mock_session.query().filter_by().first.return_value = fake_user

    monkeypatch.setattr("controllers.authentication.SessionLocal", lambda: mock_session)

    success, token = authenticate_user("test@example.com", "password123")
    assert success is True
    assert isinstance(token, str)
    payload = decode_token(token)
    assert payload["user_id"] == 1


def test_authenticate_user_failure(monkeypatch):
    mock_session = MagicMock()
    mock_session.query().filter_by().first.return_value = None

    monkeypatch.setattr("controllers.authentication.SessionLocal", lambda: mock_session)

    success, message = authenticate_user("wrong@example.com", "password")
    assert success is False
    assert message == "Email ou mot de passe incorrect."


def test_get_current_user_token_payload(tmp_path, monkeypatch):
    token = create_access_token({"user_id": 99, "role": "SUPPORT"})
    token_path = tmp_path / ".token"
    token_path.write_text(token)

    monkeypatch.setattr("builtins.open", lambda *args, **kwargs: token_path.open("r"))

    payload = get_current_user_token_payload()
    assert payload["user_id"] == 99
    assert payload["role"] == "SUPPORT"


def test_retrieve_authenticated_user(monkeypatch):
    mock_user = User(id=42, role=Department.SUPPORT)

    mock_session = MagicMock()
    mock_session.scalar.return_value = mock_user

    monkeypatch.setattr("controllers.authentication.get_current_user_token_payload", lambda: {"user_id": 42})
    user = retrieve_authenticated_user(mock_session)
    assert user.id == 42
