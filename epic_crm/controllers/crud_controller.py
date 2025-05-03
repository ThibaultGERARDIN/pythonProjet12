import sqlalchemy
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from abc import ABC, abstractmethod
from sentry_sdk import capture_message

from controllers import authentication as auth
from controllers.permissions import permission_required
from controllers.cascade_controller import CascadeDetails, CascadeResolver
from controllers import utils
from models.users import Department, User
from models.clients import Client
from models.contracts import Contract
from models.events import Event


class BaseManager(ABC):
    """
    class template to implement model managers.

    A model manager shall implement all CRUD methods to access or modify datas.
    """

    def __init__(self, session: Session, model: type) -> None:
        self._session = session
        self._model = model
        self.cascade_resolver = CascadeResolver(session)

    def get_authenticated_user(self) -> User:
        user = auth.retrieve_authenticated_user(self._session)
        if not user:
            raise PermissionError("Aucun utilisateur authentifié trouvé.")
        return user

    def create(self, obj):
        self._session.add(obj)
        self._session.commit()

        return obj

    def get_all(self):
        request = sqlalchemy.select(self._model)
        return self._session.scalars(request).all()

    def get(self, where_clause):
        request = sqlalchemy.select(self._model).where(where_clause)
        return self._session.scalars(request).all()

    def update(self, where_clause, **values):
        self._session.execute(sqlalchemy.update(self._model).where(where_clause).values(**values))
        self._session.commit()

    def delete(self, where_clause):
        self._session.execute(sqlalchemy.delete(self._model).where(where_clause))
        self._session.commit()

    @abstractmethod
    def resolve_cascade(self, objects: List[object]) -> List[CascadeDetails]:
        pass


class UserManager(BaseManager):
    """
    Manage the access to ``User`` table.
    """

    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=User)

    @permission_required(roles=Department)
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    @permission_required(roles=Department)
    def get_all(self):
        return super().get_all()

    @permission_required(roles=[Department.ACCOUNTING])
    def create(self, firstname: str, lastname: str, email: str, password: str, role: Department):
        new_user = User(
            first_name=firstname,
            last_name=lastname,
            email=email,
            hashed_password=auth.hash_password(password),
            role=role,
        )

        new_user.set_password(password)

        created_user = super().create(new_user)

        if created_user is not None:
            capture_message(
                message=f"user {auth.get_current_user_token_payload()["user_id"]} : created user {created_user.id}",
            )

        return created_user

    @permission_required(roles=[Department.ACCOUNTING])
    def update(self, where_clause, **values):

        if "email" in values:
            values["email"] = utils.validate_email(values["email"])

        if "password" in values:
            password = values.pop("password")
            hash, salt = auth.encrypt_password(password)
            values["password_hash"] = hash
            values["salt"] = salt

        super().update(where_clause, **values)

        request = sqlalchemy.select(User).where(where_clause)
        updated_users = self._session.scalars(request)

        capture_message(
            message=f"user {auth.get_current_user_token_payload()["user_id"]}"
            f" : updated users : {[user.id for user in updated_users]}",
        )

    @permission_required(roles=[Department.ACCOUNTING])
    def delete(self, where_clause):
        return super().delete(where_clause)

    def resolve_cascade(self, users: List[User]) -> List[CascadeDetails]:
        return self.cascade_resolver.resolve_user_cascade(users=users)


class ClientsManager(BaseManager):
    """
    Manage the access to ``Client`` table.
    """

    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=Client)

    @permission_required(roles=[Department.SALES])
    def create(
        self,
        email: str,
        full_name: str,
        phone: str,
        enterprise: str,
    ) -> Client:
        client = Client(
            full_name=full_name,
            email=email,
            phone=phone,
            enterprise=enterprise,
            sales_contact_id=auth.get_current_user_token_payload()["user_id"],
        )

        return super().create(client)

    @permission_required(roles=Department)
    def get(self, where_clause) -> List[Client]:
        return super().get(where_clause)

    @permission_required(roles=Department)
    def get_all(self) -> List[Client]:
        return super().get_all()

    @permission_required([Department.SALES])
    def get_my_clients(self) -> List[Client]:
        user = self.get_authenticated_user()
        return self.get(Client.sales_contact_id == user.id)

    @permission_required(roles=[Department.SALES])
    def update(self, where_clause, **values):

        user = self.get_authenticated_user()

        if user.role == Department.SALES:
            clients = self.get(where_clause)
            for client in clients:
                if client.sales_contact_id != user.id:
                    raise PermissionError("Permission denied: not your client.")

        return super().update(where_clause, **values)

    @permission_required(roles=[Department.SALES])
    def delete(self, where_clause):
        return super().delete(where_clause)

    def filter_by_name(self, name_contains: str):
        return self.get(Client.full_name.contains(name_contains))

    def resolve_cascade(self, clients: List[Client]) -> List[CascadeDetails]:
        return self.cascade_resolver.resolve_clients_cascade(clients=clients)


class ContractsManager(BaseManager):
    """
    Manage the access to ``Contract`` table.
    """

    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=Contract)

    @permission_required(roles=[Department.ACCOUNTING])
    def create(self, client_id: int, total_amount: float, to_be_paid: int, is_signed: bool):
        return super().create(
            Contract(
                client_id=client_id,
                sales_contact_id=auth.get_current_user_token_payload()["user_id"],
                total_amount=total_amount,
                to_be_paid=to_be_paid,
                is_signed=is_signed,
            )
        )

    @permission_required(roles=Department)
    def get(self, where_clause) -> List[Contract]:
        return super().get(where_clause)

    @permission_required(roles=Department)
    def get_all(self) -> List[Contract]:
        return super().get_all()

    @permission_required(roles=[Department.ACCOUNTING, Department.SALES])
    def get_unsigned_contracts(self):
        return self.get(Contract.is_signed is False)

    @permission_required(roles=[Department.ACCOUNTING, Department.SALES])
    def get_unpaid_contracts(self):
        return self.get(Contract.to_be_paid > 0)

    @permission_required(roles=[Department.ACCOUNTING, Department.SALES])
    def update(self, where_clause, **values):
        user = self.get_authenticated_user()
        if user.role == Department.SALES:
            accessed_contracts = self.get(where_clause)
            for contract in accessed_contracts:
                if contract.sales_contact_id != user.id:
                    raise PermissionError("Permission denied: not responsible for this contract.")
        return super().update(where_clause, **values)

    @permission_required(roles=[Department.ACCOUNTING, Department.SALES])
    def delete(self, where_clause):
        user = self.get_authenticated_user()
        if user.role == Department.SALES:
            accessed_contracts = self.get(where_clause)
            for contract in accessed_contracts:
                if contract.sales_contact_id != user.id:
                    raise PermissionError("Permission denied: not responsible for this contract.")
        return super().delete(where_clause)

    def resolve_cascade(self, contracts: List[Contract]) -> List[CascadeDetails]:
        return self.cascade_resolver.resolve_contracts_cascade(contracts=contracts)


class EventsManager(BaseManager):
    """
    Manage the access to ``Event`` table.
    """

    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=Event)

    @permission_required([Department.SALES])
    def create(
        self,
        start_date=datetime,
        end_date=datetime,
        location=str,
        attendees_count=int,
        notes=str,
        contract_id=int,
        support_contact_id=int,
    ):

        support_user = self._session.get(User, support_contact_id)
        utils.check_user_role(support_user, Department.SUPPORT)

        # Récupérer le contrat
        contract = self._session.get(Contract, contract_id)
        if not contract or not contract.is_signed:
            raise ValueError("Contract must exist and be signed.")

        # Vérifier que le client appartient au sales actuel
        user = self.get_authenticated_user()
        if contract.sales_contact_id != user.id:
            raise PermissionError("Permission denied: not your contract.")

        return super().create(
            Event(
                start_date=start_date,
                end_date=end_date,
                location=location,
                attendees_count=attendees_count,
                notes=notes,
                contract_id=contract_id,
                support_contact_id=support_contact_id,
            )
        )

    @permission_required(roles=Department)
    def get(self, where_clause) -> List[Event]:
        return super().get(where_clause)

    @permission_required(roles=Department)
    def get_all(self) -> List[Event]:
        return super().get_all()

    @permission_required([Department.SUPPORT])
    def get_my_events(self) -> List[Event]:
        user = self.get_authenticated_user()
        return self.get(Event.support_contact_id == user.id)

    def get_unassigned_support_events(self) -> List[Event]:
        return self.get(Event.support_contact_id is None)

    @permission_required([Department.ACCOUNTING, Department.SUPPORT])
    def update(self, where_clause, **values):

        user = self.get_authenticated_user()
        accessed_objects = self.get(where_clause)

        if user.role == Department.SUPPORT:
            for event in accessed_objects:
                if event.support_contact_id != user.id:
                    raise PermissionError(f"Permission denied. Not authorized to update event {event.id}")

        if "support_contact_id" in values:
            support_contact = self._session.get(User, values["support_contact_id"])
            utils.check_user_role(support_contact, Department.SUPPORT)

        return super().update(where_clause, **values)

    @permission_required([Department.ACCOUNTING, Department.SUPPORT])
    def delete(self, where_clause):

        user = self.get_authenticated_user()
        accessed_objects = self.get(where_clause)

        # check that support employee own the accessed events
        if user.role == Department.SUPPORT:
            for event in accessed_objects:
                if event.support_contact_id != user.id:
                    raise PermissionError(f"Permission denied. Not authorized to update event {event.id}")

        return super().delete(where_clause)

    def resolve_cascade(self, events: List[Event]) -> List[CascadeDetails]:
        return [CascadeDetails(title="EVENTS", headers=Event.HEADERS, objects=events)]
