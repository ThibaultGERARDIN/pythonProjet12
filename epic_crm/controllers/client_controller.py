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
    Manages access to the ``Client`` table, allowing creation, retrieval,
    updating, and deletion of clients. Includes permission checks based on user roles.
    """

    def __init__(self, session: Session) -> None:
        """
        Initialize the ClientsManager with a database session and bind it to the Client model.
        """
        super().__init__(session=session, model=Client)

    @permission_required(roles=[Department.SALES])
    def create(
        self,
        email: str,
        full_name: str,
        phone: str,
        enterprise: str,
    ) -> Client:
        """
        Create a new client associated with the currently authenticated sales user.

        Args:
            email (str): Email address of the client.
            full_name (str): Full name of the client.
            phone (str): Phone number of the client.
            enterprise (str): Enterprise or company name.

        Returns:
            Client: The newly created client instance.
        """
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
        """
        Retrieve all clients matching the provided condition.

        Args:
            where_clause: SQLAlchemy condition used to filter clients.

        Returns:
            List[Client]: List of matching client records.
        """
        return super().get(where_clause)

    @permission_required(roles=Department)
    def get_all(self) -> List[Client]:
        """
        Retrieve all client records.

        Returns:
            List[Client]: All clients in the database.
        """
        return super().get_all()

    @permission_required([Department.SALES])
    def get_my_clients(self) -> List[Client]:
        """
        Retrieve all clients assigned to the currently authenticated sales user.

        Returns:
            List[Client]: List of the sales user's own clients.
        """
        user = self.get_authenticated_user()
        return self.get(Client.sales_contact_id == user.id)

    @permission_required(roles=[Department.SALES])
    def update(self, where_clause, **values):
        """
        Update client records matching the provided condition. Sales users can only
        update their own clients.

        Args:
            where_clause: SQLAlchemy condition to locate clients.
            **values: Fields and values to update.

        Returns:
            int: Number of updated client records.

        Raises:
            PermissionError: If the user attempts to update a client not assigned to them.
        """

        user = self.get_authenticated_user()

        if user.role == Department.SALES:
            clients = self.get(where_clause)
            for client in clients:
                if client.sales_contact_id != user.id:
                    raise PermissionError("Permission denied: not your client.")

        return super().update(where_clause, **values)

    @permission_required(roles=[Department.SALES])
    def delete(self, where_clause):
        """
        Delete client records matching the provided condition.

        Args:
            where_clause: SQLAlchemy condition to locate clients.

        Returns:
            int: Number of deleted client records.
        """
        return super().delete(where_clause)

    def filter_by_name(self, name_contains: str):
        """
        Retrieve clients whose full name contains the given string.

        Args:
            name_contains (str): Substring to match within client names.

        Returns:
            List[Client]: Clients with names matching the substring.
        """
        return self.get(Client.full_name.contains(name_contains))

    def resolve_cascade(self, clients: List[Client]) -> List[CascadeDetails]:
        """
        Retrieve cascading dependencies related to the provided clients, such as linked contracts or events.

        Args:
            clients (List[Client]): List of clients.

        Returns:
            List[CascadeDetails]: Details about the related records for cascade handling.
        """
        return self.cascade_resolver.resolve_clients_cascade(clients=clients)
