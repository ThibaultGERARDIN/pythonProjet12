from .base import Base
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
)


class Event(Base):
    """
    ORM model representing an event associated with a client contract.

    An event is typically a planned activity such as a meeting, kickoff, or delivery session.
    Events are linked to a specific contract and client, and may be assigned to a support employee.

    Attributes:
        id (int): Primary key, auto-incremented.
        event_name (str): Title or name of the event.
        start_date (datetime): Start timestamp of the event (required).
        end_date (datetime): End timestamp of the event (required).
        location (str): Physical location where the event takes place.
        attendees (int): Number of people expected to attend the event.
        notes (str, optional): Additional notes or comments about the event.
        contract_id (int): Foreign key to the associated contract (required).
        client_id (int): Foreign key to the associated client (required).
        support_contact_id (int, optional): Foreign key to the assigned support staff (nullable).

    Relationships:
        contract (Contract): SQLAlchemy relationship to the related contract.
        client (Client): SQLAlchemy relationship to the related client.
        support_contact (User): SQLAlchemy relationship to the assigned support user.

    Properties:
        duration_hours (float): Total duration of the event in hours.

    Constants:
        HEADERS (Tuple[str]): Tuple of field names used for tabular export.

    Methods:
        to_list(): Returns the event’s data as a tuple, suitable for tabular display or export.
    """

    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)

    event_name = Column(String(150), nullable=False)

    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    location = Column(String(255), nullable=False)
    attendees = Column(Integer, nullable=False)
    notes = Column(String(1000), nullable=True)

    contract_id = Column(
        Integer,
        ForeignKey("contracts.id", ondelete="CASCADE"),
        nullable=False,
    )
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)

    support_contact_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )

    contract = relationship("Contract", back_populates="events")
    client = relationship("Client", back_populates="events")
    support_contact = relationship("User", back_populates="events")

    @property
    def duration_hours(self):
        return (self.end_date - self.start_date).total_seconds() / 3600

    HEADERS = (
        "id",
        "event_name",
        "start_date",
        "end_date",
        "location",
        "attendees",
        "notes",
        "contract_id",
        "client_id",
        "support_contact_id",
    )

    def to_list(self):
        return (
            self.id,
            self.event_name,
            self.start_date,
            self.end_date,
            self.location,
            self.attendees,
            self.notes,
            self.contract_id,
            self.client_id,
            self.support_contact_id,
        )
