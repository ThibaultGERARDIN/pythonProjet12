import pytest
from unittest.mock import MagicMock
from controllers.permissions import resolve_permission, permission_required
from models.users import Department, User


@pytest.fixture
def mock_user_sales():
    return User(
        id=2, first_name="Test", last_name="Sales", email="sales@test.com", hashed_password="123", role=Department.SALES
    )


@pytest.fixture
def mock_user_support():
    return User(
        id=3,
        first_name="Test",
        last_name="Support",
        email="support@test.com",
        hashed_password="123",
        role=Department.SUPPORT,
    )


@pytest.fixture
def mock_user_accounting():
    return User(
        id=1,
        first_name="Test",
        last_name="Accounting",
        email="acc@test.com",
        hashed_password="123",
        role=Department.ACCOUNTING,
    )


def test_resolve_permission_valid_sales(monkeypatch, mock_auth_sales, mock_user_sales):
    fake_session = MagicMock()
    fake_session.get.return_value = mock_user_sales
    monkeypatch.setattr("controllers.permissions.SessionLocal", lambda: fake_session)

    def dummy_function(x):
        return x * 2

    result = resolve_permission([Department.SALES], dummy_function, 5)
    assert result == 10


def test_resolve_permission_denied(monkeypatch, mock_auth_sales, mock_user_sales):
    fake_session = MagicMock()
    fake_session.get.return_value = mock_user_sales
    monkeypatch.setattr("controllers.permissions.SessionLocal", lambda: fake_session)

    def dummy_function(x):
        return x + 1

    with pytest.raises(PermissionError, match="Permission denied"):
        resolve_permission([Department.SUPPORT], dummy_function, 5)


def test_permission_required_decorator(monkeypatch, mock_auth_accounting, mock_user_accounting):
    fake_session = MagicMock()
    fake_session.get.return_value = mock_user_accounting
    monkeypatch.setattr("controllers.permissions.SessionLocal", lambda: fake_session)

    @permission_required([Department.ACCOUNTING])
    def protected_func(x):
        return x * 3

    assert protected_func(4) == 12


def test_permission_required_decorator_denied(monkeypatch, mock_auth_support, mock_user_support):
    fake_session = MagicMock()
    fake_session.get.return_value = mock_user_support
    monkeypatch.setattr("controllers.permissions.SessionLocal", lambda: fake_session)

    @permission_required([Department.SALES])
    def protected_func(x):
        return x * 3

    with pytest.raises(PermissionError, match="Permission denied"):
        protected_func(4)
