import sqlalchemy
from sqlalchemy.orm import Session
from typing import List, Any

from models.users import User
from models.clients import Client
from models.contracts import Contract
from models.events import Event
from tabulate import tabulate


class CascadeDetails:
    """
    Data object storing details about entities affected by a deletion cascade.

    Used to represent related objects (e.g. users, clients, contracts, events)
    that would be impacted if a particular object were deleted.
    """

    def __init__(self, title: str, headers: List[str], objects: List[Any]) -> None:
        """
        Initialize a CascadeDetails object.

        Args:
            title (str): The title describing the category of objects (e.g. 'USERS').
            headers (List[str]): Table headers for display.
            objects (List[Any]): List of ORM model instances.
        """
        self.title = title
        self.objects = objects
        self.headers = headers

    def not_none_objects(self) -> List[object]:
        """
        Filter out None values from the object list.

        Returns:
            List[object]: List of non-null objects.
        """
        return [obj for obj in self.objects if obj is not None]

    def __str__(self):
        """
        Return a formatted string representation of the cascade details, suitable for display.
        """
        objects = self.not_none_objects()
        return "\n".join([self.title, tabulate(tabular_data=[obj.to_list() for obj in objects], headers=self.headers)])

    def __repr__(self) -> str:
        """
        Return the string representation of the object for debugging.
        """
        return self.__str__()


class CascadeResolver:
    """
    Handles the logic for retrieving related objects affected by deletions (cascade dependencies),
    such as events linked to contracts or contracts linked to clients or users.
    """

    def __init__(self, session: Session) -> None:
        """
        Initialize the resolver with a SQLAlchemy session.

        Args:
            session (Session): SQLAlchemy session used for queries.
        """
        self.session = session

    def _retreive_clients_from_users(self, users: List[User]) -> List[Client]:
        """
        Retrieve all clients associated with the given users.

        Args:
            users (List[User]): List of users.

        Returns:
            List[Client]: List of clients linked to those users.
        """

        clients = []
        for user in users:
            if user is None:
                continue
            clients.extend(
                self.session.scalars(sqlalchemy.select(Client).where(Client.sales_contact_id == user.id)).all()
            )
        return clients

    def _retreive_contracts_from_users(self, users: List[User]) -> List[Contract]:
        """
        Retrieve all contracts where the given users are assigned as sales contacts.

        Args:
            users (List[User]): List of users.

        Returns:
            List[Contract]: List of associated contracts.
        """
        contracts = []
        for user in users:
            if user is None:
                continue
            contracts.extend(
                self.session.scalars(sqlalchemy.select(Contract).where(Contract.sales_contact_id == user.id)).all()
            )
        return contracts

    def _retreive_events_from_user(self, users: List[User]) -> List[Event]:
        """
        Retrieve all events where the given users are assigned as support contacts.

        Args:
            users (List[User]): List of users.

        Returns:
            List[Event]: List of associated events.
        """
        events = []
        for user in users:
            if user is None:
                continue
            events.extend(
                self.session.scalars(sqlalchemy.select(Event).where(Event.support_contact_id == user.id)).all()
            )
        return events

    def _retreive_contracts_from_clients(self, clients: List[Client]) -> List[Contract]:
        """
        Retrieve all contracts linked to the provided clients.

        Args:
            clients (List[Client]): List of clients.

        Returns:
            List[Contract]: List of associated contracts.
        """
        contracts = []
        for client in clients:
            if client is None:
                continue
            contracts.extend(
                self.session.scalars(sqlalchemy.select(Contract).where(Contract.client_id == client.id)).all()
            )
        return contracts

    def _retreive_events_from_contracts(self, contracts: List[Contract]) -> List[Event]:
        """
        Retrieve all events linked to the provided contracts.

        Args:
            contracts (List[Contract]): List of contracts.

        Returns:
            List[Event]: List of associated events.
        """
        events = []
        for contract in contracts:
            if contract is None:
                continue
            events.extend(self.session.scalars(sqlalchemy.select(Event).where(Event.contract_id == contract.id)).all())
        return events

    def resolve_user_cascade(self, users: List[User]) -> List[CascadeDetails]:
        """
        Resolve all entities that would be affected by the deletion of the given users.

        Returns:
            List[CascadeDetails]: Cascade details including clients, contracts, and events.
        """
        clients = self._retreive_clients_from_users(users)
        contracts = self._retreive_contracts_from_users(users) + self._retreive_contracts_from_clients(clients)
        events = self._retreive_events_from_user(users) + self._retreive_events_from_contracts(contracts)
        return [
            CascadeDetails(
                title="userS",
                headers=User.HEADERS,
                objects=users,
            ),
            CascadeDetails(
                title="CLIENTS",
                headers=Client.HEADERS,
                objects=clients,
            ),
            CascadeDetails(
                title="CONTRACTS",
                headers=Contract.HEADERS,
                objects=contracts,
            ),
            CascadeDetails(title="EVENTS", headers=Event.HEADERS, objects=events),
        ]

    def resolve_clients_cascade(self, clients: List[Client]) -> List[CascadeDetails]:
        """
        Resolve all entities that would be affected by the deletion of the given clients.

        Returns:
            List[CascadeDetails]: Cascade details including contracts and events.
        """
        contracts = self._retreive_contracts_from_clients(clients)
        events = self._retreive_events_from_contracts(contracts)
        return [
            CascadeDetails(
                title="CLIENTS",
                headers=Client.HEADERS,
                objects=clients,
            ),
            CascadeDetails(title="CONTRACTS", headers=Contract.HEADERS, objects=contracts),
            CascadeDetails(title="EVENTS", headers=Event.HEADERS, objects=events),
        ]

    def resolve_contracts_cascade(self, contracts: List[Contract]) -> List[CascadeDetails]:
        """
        Resolve all entities that would be affected by the deletion of the given contracts.

        Returns:
            List[CascadeDetails]: Cascade details including related events.
        """
        events = self._retreive_events_from_contracts(contracts)
        return [
            CascadeDetails(
                title="CONTRACTS",
                headers=Contract.HEADERS,
                objects=contracts,
            ),
            CascadeDetails(
                title="EVENTS",
                headers=Event.HEADERS,
                objects=events,
            ),
        ]
