from sqlalchemy.orm import relationship
from sqlalchemy import Enum, Column, Integer, String
import enum
from .base import Base


class Department(enum.Enum):
    SALES = "sales"
    ACCOUNTING = "accounting"
    SUPPORT = "support"


class User(Base):
    """
    ORM model representing a system user.

    A user can belong to one of the departments: SALES, ACCOUNTING, or SUPPORT.
    Depending on their role, users may manage clients, sign contracts, or support events.

    Attributes:
        id (int): Primary key, auto-incremented.
        first_name (str): First name of the user (required).
        last_name (str): Last name of the user (required).
        email (str): Unique email address used for login (required).
        hashed_password (str): Hashed password for authentication (required).
        role (Department): Enum representing the user's department/role (required).

    Relationships:
        clients (List[Client]): Clients managed by the user (if role is SALES).
        contracts (List[Contract]): Contracts created by or assigned to the user (if role is SALES).
        events (List[Event]): Events supported by the user (if role is SUPPORT).

    Constants:
        HEADERS (List[str]): Column headers used for exporting user data in tabular format.

    Properties:
        full_name (str): Concatenated first and last name of the user.

    Methods:
        to_list(): Returns a tuple representation of the user for display or export purposes.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)

    first_name = Column(String(50), nullable=False)

    last_name = Column(String(50), nullable=False)

    email = Column(String(100), unique=True, nullable=False)

    hashed_password = Column(String(255), nullable=False)

    role = Column(Enum(Department), nullable=False)

    clients = relationship("Client", back_populates="sales_contact")
    contracts = relationship("Contract", back_populates="sales_contact")
    events = relationship("Event", back_populates="support_contact")

    HEADERS = ["id", "email", "full_name", "role"]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def to_list(self):
        return (
            self.id,
            self.email,
            self.full_name,
            self.role.name,
        )
