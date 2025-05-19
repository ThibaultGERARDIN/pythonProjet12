import pytest
from unittest.mock import patch
from controllers.contract_controller import ContractsManager
from models.contracts import Contract
from models.clients import Client
from models.users import Department, User


@pytest.fixture
def sales_user():
    return User(
        id=2,
        email="sales@epic.com",
        first_name="S",
        last_name="U",
        hashed_password="pwd",
        role=Department.SALES,
    )


@pytest.fixture
def client_for_contract():
    return Client(
        id=1,
        sales_contact_id=2,
        full_name="Client Test",
        email="client@test.com",
        phone="0600000000",
        enterprise="TestCorp",
    )


@patch("controllers.permissions.SessionLocal")
def test_create_contract(mock_sessionlocal, dummy_session, sales_user, client_for_contract, mock_auth_sales):
    dummy_session.data = [sales_user, client_for_contract]
    dummy_session.scalar_return_value = sales_user
    mock_sessionlocal.return_value = dummy_session

    manager = ContractsManager(dummy_session)
    contract = manager.create(
        client_id=1,
        total_amount=1000.0,
        to_be_paid=500,
        is_signed=True,
    )

    assert isinstance(contract, Contract)
    assert contract.client_id == 1
    assert contract.sales_contact_id == sales_user.id
    assert contract in dummy_session.added


@patch("controllers.permissions.SessionLocal")
def test_get_all_contracts(mock_sessionlocal, dummy_session, mock_auth_sales, sales_user):
    dummy_session.scalar_return_value = sales_user
    dummy_session.get_return_value = sales_user
    mock_sessionlocal.return_value = dummy_session

    contract = Contract(id=1, client_id=1, sales_contact_id=2, total_amount=1000, to_be_paid=500, is_signed=False)
    dummy_session.data = [contract]

    manager = ContractsManager(dummy_session)
    result = manager.get_all()

    assert contract in result


@patch("controllers.permissions.SessionLocal")
def test_get_with_clause(mock_sessionlocal, dummy_session, mock_auth_sales, sales_user):
    dummy_session.scalar_return_value = sales_user
    dummy_session.get_return_value = sales_user
    mock_sessionlocal.return_value = dummy_session

    contract = Contract(id=2, client_id=1, sales_contact_id=2, total_amount=2000, to_be_paid=0, is_signed=True)
    dummy_session.data = [contract]

    manager = ContractsManager(dummy_session)
    result = manager.get(Contract.id == 2)

    assert result == [contract]


@patch("controllers.permissions.SessionLocal")
def test_update_contract(mock_sessionlocal, dummy_session, sales_user, mock_auth_sales):
    dummy_session.get_return_value = sales_user
    dummy_session.scalar_return_value = sales_user
    mock_sessionlocal.return_value = dummy_session

    contract = Contract(id=3, client_id=1, sales_contact_id=2, total_amount=3000, to_be_paid=1500, is_signed=False)
    dummy_session.data = [contract]
    manager = ContractsManager(dummy_session)
    manager.update(Contract.id == 3, to_be_paid=1000)
    assert len(dummy_session.updated) == 1


@patch("controllers.permissions.SessionLocal")
def test_delete_contract(mock_sessionlocal, dummy_session, sales_user, mock_auth_sales):
    dummy_session.get_return_value = sales_user
    dummy_session.scalar_return_value = sales_user
    mock_sessionlocal.return_value = dummy_session

    contract = Contract(id=4, client_id=1, sales_contact_id=2, total_amount=1500, to_be_paid=0, is_signed=True)
    dummy_session.data = [contract]
    manager = ContractsManager(dummy_session)
    manager.delete(Contract.id == 4)
    assert len(dummy_session.updated) == 1
