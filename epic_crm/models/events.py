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
        nullable=False,
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
