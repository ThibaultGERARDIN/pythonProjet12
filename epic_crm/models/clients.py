from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
)

from .base import Base


class Client(Base):
    """
    ORM model representing a client entity in the system.

    A client is associated with a sales contact (User) and may have multiple contracts and events.
    This model supports cascade deletion for related events when a client is removed.

    Attributes:
        id (int): Primary key, auto-incremented.
        full_name (str): Full name of the client (required).
        email (str): Unique email address of the client (required).
        phone (str): Unique phone number of the client (required).
        enterprise (str): Name of the client’s company.
        creation_date (datetime): Timestamp of when the client was created (automatically set).
        last_update (datetime): Timestamp of last update (automatically set on modification).
        sales_contact_id (int): Foreign key to the assigned sales contact (required).
        sales_contact (User): SQLAlchemy relationship to the assigned sales contact.
        events (List[Event]): Events associated with the client. Deleting the client deletes related events.
        contracts (List[Contract]): Contracts linked to this client.

    Constants:
        HEADERS (Tuple[str]): List of field names used for tabular export.

    Methods:
        to_list(): Returns the client’s information as a tuple of values, for tabular display or export.
    """
    __tablename__ = "clients"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    full_name = Column(String(100), nullable=False)

    email = Column(
        String(100),
        nullable=False,
        unique=True,
    )

    phone = Column(
        String(15),
        nullable=False,
        unique=True,
    )

    enterprise = Column(String(100))

    creation_date = Column(DateTime(timezone=True), server_default=func.now())

    last_update = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
    )

    sales_contact_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    sales_contact = relationship(
        "User",
        cascade="all,delete",
    )
    events = relationship("Event", back_populates="client", cascade="all, delete-orphan")
    contracts = relationship("Contract", back_populates="client")

    HEADERS = (
        "id",
        "full_name",
        "email",
        "phone",
        "enterprise",
        "creation_date",
        "last_update",
        "sales_contact_id",
    )

    def to_list(self):
        return (
            self.id,
            self.full_name,
            self.email,
            self.phone,
            self.enterprise,
            self.creation_date,
            self.last_update,
            self.sales_contact_id,
        )
