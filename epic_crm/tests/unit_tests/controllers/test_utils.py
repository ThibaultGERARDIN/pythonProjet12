import pytest
from controllers.utils import validate_email
from models.users import Department, User
from controllers.utils import check_user_role


def test_validate_email_valid():
    assert validate_email("test.email@domain.com") == "test.email@domain.com"


def test_validate_email_invalid():
    with pytest.raises(ValueError):
        validate_email("invalid-email")


def test_check_user_role_valid():
    user = User(first_name="A", last_name="B", email="a@b.com", hashed_password="123", role=Department.SUPPORT)
    assert check_user_role(user, Department.SUPPORT) is None  # pas d'erreur levée


def test_check_user_role_invalid():
    user = User(first_name="A", last_name="B", email="a@b.com", hashed_password="123", role=Department.SALES)
    with pytest.raises(ValueError):
        check_user_role(user, Department.SUPPORT)
