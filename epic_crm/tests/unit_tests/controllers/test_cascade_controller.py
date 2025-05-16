import pytest
from controllers.cascade_controller import CascadeResolver
from models.users import User, Department
from models.clients import Client
from models.contracts import Contract
from models.events import Event


def test_resolve_user_cascade(test_db_session, setup_database):
    sales_user = User(
        first_name="Jean",
        last_name="Dupont",
        email="jean@sales.com",
        hashed_password="hashed",
        role=Department.SALES,
    )
    test_db_session.add(sales_user)
    test_db_session.commit()

    client = Client(
        full_name="Test Client",
        email="client@test.com",
        phone="0600000000",
        enterprise="TestCorp",
        sales_contact_id=sales_user.id,
    )
    test_db_session.add(client)
    test_db_session.commit()

    contract = Contract(
        client_id=client.id,
        sales_contact_id=sales_user.id,
        total_amount=1000,
        to_be_paid=500,
        is_signed=True,
    )
    test_db_session.add(contract)
    test_db_session.commit()

    event = Event(
        event_name="Test Event",
        start_date="2025-01-01",
        end_date="2025-01-02",
        location="Paris",
        attendees=20,
        notes="Préparation",
        contract_id=contract.id,
        support_contact_id=sales_user.id,
        client_id=client.id,
    )
    test_db_session.add(event)
    test_db_session.commit()

    resolver = CascadeResolver(test_db_session)
    cascade = resolver.resolve_user_cascade([sales_user])
    assert cascade
    assert any(d.title == "CLIENTS" for d in cascade)
    assert any(d.title == "CONTRACTS" for d in cascade)
    assert any(d.title == "EVENTS" for d in cascade)


def test_resolve_contracts_cascade(test_db_session, setup_database):
    contract = test_db_session.query(Contract).first()
    resolver = CascadeResolver(test_db_session)
    cascade = resolver.resolve_contracts_cascade([contract])
    assert cascade
    assert any(d.title == "EVENTS" for d in cascade)


def test_resolve_clients_cascade(test_db_session, setup_database):
    client = test_db_session.query(Client).first()
    resolver = CascadeResolver(test_db_session)
    cascade = resolver.resolve_clients_cascade([client])
    assert cascade
    assert any(d.title == "CONTRACTS" for d in cascade)
    assert any(d.title == "EVENTS" for d in cascade)
