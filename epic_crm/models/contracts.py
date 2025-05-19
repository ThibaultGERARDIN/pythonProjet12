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
    """
    ORM model representing a contract between a client and the company.

    A contract is linked to a client and assigned to a sales representative.
    It tracks the total value, remaining balance, signature status, and is related to any events
    organized under its scope.

    Attributes:
        id (int): Primary key, auto-incremented.
        total_amount (float): Total value of the contract in euros.
        to_be_paid (float): Remaining amount to be paid.
        creation_date (datetime): Timestamp of when the contract was created (automatically set).
        last_update (datetime): Timestamp of last update (automatically set on modification).
        is_signed (bool): Indicates whether the contract has been signed.
        client_id (int): Foreign key referencing the associated client (required).
        sales_contact_id (int): Foreign key referencing the responsible sales representative (required).
        client (Client): SQLAlchemy relationship to the associated client.
        sales_contact (User): SQLAlchemy relationship to the sales contact.
        events (List[Event]): Events related to this contract. Deleting the contract removes related events.

    Properties:
        is_fully_paid (bool): Returns True if the remaining amount to be paid is zero.

    Constants:
        HEADERS (Tuple[str]): List of field names used for tabular export.

    Methods:
        to_list(): Returns the contract’s data as a tuple, suitable for tabular display or export.
    """

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
