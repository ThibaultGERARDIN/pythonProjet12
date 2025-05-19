import pytest
from unittest.mock import patch
from controllers.client_controller import ClientsManager
from models.users import Department, User
from models.clients import Client


@pytest.fixture
def sales_user():
    return User(
        id=2, email="sales@epic.com", role=Department.SALES, first_name="S", last_name="U", hashed_password="pwd"
    )


@patch("controllers.permissions.SessionLocal")
def test_create_client(mock_sessionlocal, dummy_session, sales_user, token_file, mock_auth_sales):
    dummy_session.scalar_return_value = sales_user
    dummy_session.get_return_value = sales_user
    mock_sessionlocal.return_value = dummy_session

    def dummy_get(model, id_):
        if model == User and id_ == 2:
            return sales_user
        return None

    dummy_session.get = dummy_get

    manager = ClientsManager(dummy_session)
    client = manager.create(
        email="client@corp.com",
        full_name="Client Corp",
        phone="0600000000",
        enterprise="Corp",
    )

    assert isinstance(client, Client)
    assert client.sales_contact_id == 2
    assert client in dummy_session.added


@patch("controllers.permissions.SessionLocal")
def test_get_all_clients(mock_sessionlocal, dummy_session, mock_auth_sales, sales_user):
    dummy_session.scalar_return_value = sales_user
    dummy_session.get_return_value = sales_user
    mock_sessionlocal.return_value = dummy_session

    client = Client(email="a@a.com", full_name="A A", phone="0611111111", enterprise="A")
    dummy_session.data = [client]

    manager = ClientsManager(dummy_session)
    assert client in manager.get_all()


@patch("controllers.permissions.SessionLocal")
def test_get_clients_with_clause(mock_sessionlocal, dummy_session, mock_auth_sales, sales_user):
    dummy_session.scalar_return_value = sales_user
    dummy_session.get_return_value = sales_user
    mock_sessionlocal.return_value = dummy_session

    client = Client(id=1, email="client@corp.com", full_name="Client Corp", phone="0622222222", enterprise="Corp")
    dummy_session.data = [client]

    manager = ClientsManager(dummy_session)
    result = manager.get(Client.id == 1)

    assert result == [client]


@patch("controllers.permissions.SessionLocal")
def test_update_own_client(mock_sessionlocal, dummy_session, mock_auth_sales, sales_user):
    dummy_session.scalar_return_value = sales_user
    dummy_session.get_return_value = sales_user
    mock_sessionlocal.return_value = dummy_session

    client = Client(id=3, sales_contact_id=2)
    dummy_session.data = [client]

    manager = ClientsManager(dummy_session)
    manager.update(Client.id == 3, phone="0601234567")

    assert len(dummy_session.updated) == 1


@patch("controllers.permissions.SessionLocal")
def test_update_other_sales_client_forbidden(mock_sessionlocal, dummy_session, mock_auth_sales, sales_user):
    dummy_session.scalar_return_value = sales_user
    dummy_session.get_return_value = sales_user
    mock_sessionlocal.return_value = dummy_session

    client = Client(id=4, sales_contact_id=99)  # Différent de l’ID user
    dummy_session.data = [client]

    manager = ClientsManager(dummy_session)
    with pytest.raises(PermissionError):
        manager.update(Client.id == 4, phone="0609876543")


@patch("controllers.permissions.SessionLocal")
def test_delete_client(mock_sessionlocal, dummy_session, mock_auth_sales, sales_user):
    dummy_session.scalar_return_value = sales_user
    dummy_session.get_return_value = sales_user
    mock_sessionlocal.return_value = dummy_session

    client = Client(id=1, sales_contact_id=2)
    dummy_session.data = [client]

    manager = ClientsManager(dummy_session)
    manager.delete(Client.id == 1)

    assert len(dummy_session.updated) == 1
