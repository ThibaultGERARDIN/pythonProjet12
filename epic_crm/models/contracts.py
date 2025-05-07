from .base import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import (
    Column,
    Integer,
    Float,
    DateTime,
    Boolean,
    ForeignKey,
)


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, autoincrement=True)

    total_amount = Column(Float(precision=2))

    to_be_paid = Column(Float(precision=2))

    creation_date = Column(DateTime(timezone=True), server_default=func.now())

    last_update = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
    )

    is_signed = Column(Boolean(), default=False)

    client_id = Column(
        Integer,
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
    )

    sales_contact_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    client = relationship("Client", back_populates="contracts")

    sales_contact = relationship(
        "User",
        cascade="all,delete",
    )

    events = relationship("Event", back_populates="contract", cascade="all, delete-orphan")

    @property
    def is_fully_paid(self):
        return self.to_be_paid == 0

    HEADERS = (
        "id",
        "creation_date",
        "total_amount",
        "to_be_paid",
        "is_signed",
        "client_id",
        "sales_contact_id",
    )

    def to_list(self):
        return (
            self.id,
            self.creation_date,
            self.total_amount,
            self.to_be_paid,
            self.is_signed,
            self.client_id,
            self.sales_contact_id,
        )
