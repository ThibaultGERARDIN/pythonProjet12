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
