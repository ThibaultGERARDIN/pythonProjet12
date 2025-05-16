from sqlalchemy.orm import Session
from typing import List
from controllers.authentication import get_current_user_token_payload
from controllers.permissions import permission_required
from controllers.base_controller import BaseManager
from controllers.cascade_controller import CascadeDetails
from models.users import Department
from models.clients import Client


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
            sales_contact_id=get_current_user_token_payload()["user_id"],
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
