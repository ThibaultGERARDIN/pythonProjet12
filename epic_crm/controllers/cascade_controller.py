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
    Data object storing deletion cascade details.
    """

    def __init__(self, title: str, headers: List[str], objects: List[Any]) -> None:
        self.title = title
        self.objects = objects
        self.headers = headers

    def not_none_objects(self) -> List[object]:
        return [obj for obj in self.objects if obj is not None]

    def __str__(self):
        objects = self.not_none_objects()
        return "\n".join([self.title, tabulate(tabular_data=[obj.to_list() for obj in objects], headers=self.headers)])

    def __repr__(self) -> str:
        return self.__str__()


class CascadeResolver:
    """
    Wrapper handling the logical of deletion cascades retreiving
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def _retreive_clients_from_users(self, users: List[User]) -> List[Client]:

        clients = []

        for user in users:

            if user is None:
                continue

            clients.extend(
                self.session.scalars(sqlalchemy.select(Client).where(Client.sales_contact_id == user.id)).all()
            )

        return clients

    def _retreive_contracts_from_users(self, users: List[User]) -> List[Contract]:

        contracts = []

        for user in users:

            if user is None:
                continue

            contracts.extend(
                self.session.scalars(sqlalchemy.select(Contract).where(Contract.sales_contact_id == user.id)).all()
            )

        return contracts

    def _retreive_events_from_user(self, users: List[User]) -> List[Event]:

        events = []

        for user in users:
            if user is None:
                continue

            events.extend(
                self.session.scalars(sqlalchemy.select(Event).where(Event.support_contact_id == user.id)).all()
            )

        return events

    def _retreive_contracts_from_clients(self, clients: List[Client]) -> List[Contract]:

        contracts = []

        for client in clients:

            if client is None:
                continue

            contracts.extend(
                self.session.scalars(sqlalchemy.select(Contract).where(Contract.client_id == client.id)).all()
            )

        return contracts

    def _retreive_events_from_contracts(self, contracts: List[Contract]) -> List[Event]:

        events = []

        for contract in contracts:

            if contract is None:
                continue

            events.extend(self.session.scalars(sqlalchemy.select(Event).where(Event.contract_id == contract.id)).all())

        return events

    def resolve_user_cascade(self, users: List[User]) -> List[CascadeDetails]:

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
