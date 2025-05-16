import pytest
from unittest.mock import patch
from controllers.event_controller import EventsManager
from models.events import Event
from models.users import User, Department
from models.contracts import Contract


@pytest.fixture
def sales_user():
    return User(
        id=2, email="sales@epic.com", role=Department.SALES, first_name="S", last_name="U", hashed_password="pwd"
    )


@pytest.fixture
def support_user():
    return User(
        id=5, email="support@epic.com", role=Department.SUPPORT, first_name="P", last_name="T", hashed_password="pwd"
    )


@pytest.fixture
def event_contract():
    return Contract(id=1, client_id=3, sales_contact_id=2, total_amount=1000, to_be_paid=0, is_signed=True)


@patch("controllers.permissions.SessionLocal")
def test_create_event(mock_sessionlocal, dummy_session, sales_user, support_user, event_contract, mock_auth_sales):
    dummy_session.scalar_return_value = sales_user
    mock_sessionlocal.return_value = dummy_session

    # Redéfinir dummy_session.get() selon le modèle et l'id
    def dummy_get(model, id_):
        if model == User and id_ == 5:
            return support_user
        if model == User and id_ == 2:
            return sales_user
        if model == Contract and id_ == 1:
            return event_contract
        return None

    dummy_session.get = dummy_get

    manager = EventsManager(dummy_session)
    event = manager.create(
        event_name="test event",
        contract_id=1,
        support_contact_id=5,
        attendees=20,
        start_date="2025-10-10",
        end_date="2025-10-11",
        location="Paris",
        notes="Initial meeting",
    )

    assert isinstance(event, Event)
    assert event.contract_id == 1
    assert event.support_contact_id == 5
    assert event in dummy_session.added


@patch("controllers.permissions.SessionLocal")
def test_get_all_events(mock_sessionlocal, dummy_session, support_user, mock_auth_support):
    dummy_session.scalar_return_value = support_user
    dummy_session.get_return_value = support_user
    mock_sessionlocal.return_value = dummy_session

    event = Event(
        id=1,
        contract_id=1,
        support_contact_id=5,
        attendees=10,
        start_date="2025-12-12",
        end_date="2025-12-12",
        notes="Préparation",
    )
    dummy_session.data = [event]

    manager = EventsManager(dummy_session)
    results = manager.get_all()
    assert results == [event]


@patch("controllers.permissions.SessionLocal")
def test_update_event(mock_sessionlocal, dummy_session, support_user, mock_auth_support):
    dummy_session.scalar_return_value = support_user
    dummy_session.get_return_value = support_user
    mock_sessionlocal.return_value = dummy_session

    event = Event(
        id=2,
        contract_id=2,
        support_contact_id=5,
        attendees=30,
        start_date="2025-11-15",
        end_date="2025-11-16",
        notes="Préparation",
    )
    dummy_session.data = [event]

    manager = EventsManager(dummy_session)
    manager.update(Event.id == 2, notes="Updated note")
    assert len(dummy_session.updated) == 1


@patch("controllers.permissions.SessionLocal")
def test_delete_event(mock_sessionlocal, dummy_session, support_user, mock_auth_support):
    dummy_session.scalar_return_value = support_user
    dummy_session.get_return_value = support_user
    mock_sessionlocal.return_value = dummy_session

    event = Event(
        id=3,
        contract_id=3,
        support_contact_id=5,
        attendees=40,
        start_date="2025-12-01",
        end_date="2025-12-01",
        notes="À supprimer",
    )
    dummy_session.data = [event]

    manager = EventsManager(dummy_session)
    manager.delete(Event.id == 3)
    assert len(dummy_session.updated) == 1
