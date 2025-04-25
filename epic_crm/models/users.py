from sqlalchemy.orm import relationship
from sqlalchemy import Enum, Column, Integer, String
import enum
from .base import Base


class Department(enum.Enum):
    SALES = "sales"
    ACCOUNTING = "accounting"
    SUPPORT = "support"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)

    first_name = Column(String(50), nullable=False)

    last_name = Column(String(50), nullable=False)

    full_name = first_name + " " + last_name

    email = Column(String(100), unique=True, nullable=False)

    hashed_password = Column(String(255), nullable=False)

    role = Column(Enum(Department), nullable=False)

    clients = relationship("Client", back_populates="sales_contact")
    contracts = relationship("Contract", back_populates="sales_contact")
    events = relationship("Event", back_populates="support_contact")

    HEADERS = ["id", "email", "full_name", "role"]

    def to_list(self):
        return (
            self.id,
            self.email,
            self.full_name,
            self.role.name,
        )
