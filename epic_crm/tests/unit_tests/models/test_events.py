from models.events import Event
from datetime import datetime


def test_event_to_list():
    event = Event(
        id=7,
        event_name="Salon Tech",
        start_date=datetime(2025, 6, 1, 10, 0),
        end_date=datetime(2025, 6, 2, 18, 0),
        location="Paris Expo",
        attendees=150,
        notes="Important client event.",
        contract_id=3,
        client_id=2,
        support_contact_id=4
    )

    result = event.to_list()
    assert isinstance(result, tuple)
    assert result[0] == 7
    assert result[1] == "Salon Tech"
    assert result[5] == 150
