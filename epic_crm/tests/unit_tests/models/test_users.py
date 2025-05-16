from models.users import User, Department


def test_full_name_property():
    user = User(
        first_name="John", last_name="Doe", email="john@example.com", hashed_password="pwd", role=Department.SALES
    )
    assert user.full_name == "John Doe"


def test_to_list_returns_expected_format():
    user = User(
        id=42,
        first_name="Alice",
        last_name="Martin",
        email="alice@epic.com",
        hashed_password="xxx",
        role=Department.SUPPORT,
    )
    result = user.to_list()

    assert isinstance(result, tuple)
    assert result == (42, "alice@epic.com", "Alice Martin", "SUPPORT")


def test_user_role_enum():
    assert Department.SALES.name == "SALES"
    assert Department.SALES.value == "sales"
    assert str(Department.ACCOUNTING) == "Department.ACCOUNTING"
    assert Department.SUPPORT.value == "support"
