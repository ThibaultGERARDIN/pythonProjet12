from sqlalchemy.orm import Session
from typing import List
from controllers.permissions import permission_required
from controllers.base_controller import BaseManager
from controllers.cascade_controller import CascadeDetails
from models.users import Department
from models.clients import Client
from models.contracts import Contract


class ContractsManager(BaseManager):
    """
    Manages access to the ``Contract`` table, including creation, retrieval,
    update, and deletion of contract records. Enforces permission rules based on user roles.
    """

    def __init__(self, session: Session) -> None:
        """
        Initialize the ContractsManager with a database session and bind it to the Contract model.
        """
        super().__init__(session=session, model=Contract)

    @permission_required(roles=[Department.ACCOUNTING, Department.SALES])
    def create(self, client_id: int, total_amount: float, to_be_paid: int, is_signed: bool):
        """
        Create a new contract linked to a client, ensuring the client is assigned to the current user.

        Args:
            client_id (int): ID of the client associated with the contract.
            total_amount (float): Total amount of the contract.
            to_be_paid (int): Remaining unpaid amount.
            is_signed (bool): Indicates if the contract is signed.

        Returns:
            Contract: The newly created contract instance.

        Raises:
            ValueError: If the client is not found.
            PermissionError: If the current user is not the assigned sales contact.
        """
        user = self.get_authenticated_user()

        client = self._session.get(Client, client_id)
        if not client:
            raise ValueError("Client non trouvé.")
        if client.sales_contact_id != user.id:
            raise PermissionError("Ce client ne vous est pas assigné.")

        return super().create(
            Contract(
                client_id=client_id,
                sales_contact_id=client.sales_contact_id,
                total_amount=total_amount,
                to_be_paid=to_be_paid,
                is_signed=is_signed,
            )
        )

    @permission_required(roles=Department)
    def get(self, where_clause) -> List[Contract]:
        """
        Retrieve all contracts matching the given condition.

        Args:
            where_clause: SQLAlchemy condition to filter contracts.

        Returns:
            List[Contract]: List of contracts matching the condition.
        """
        return super().get(where_clause)

    @permission_required(roles=Department)
    def get_all(self) -> List[Contract]:
        """
        Retrieve all contracts from the database.

        Returns:
            List[Contract]: List of all contract entries.
        """
        return super().get_all()

    @permission_required(roles=[Department.ACCOUNTING, Department.SALES])
    def get_unsigned_contracts(self):
        """
        Retrieve all contracts that are not signed.

        Returns:
            List[Contract]: List of unsigned contracts.
        """
        return self.get(Contract.is_signed is False)

    @permission_required(roles=[Department.ACCOUNTING, Department.SALES])
    def get_unpaid_contracts(self):
        """
        Retrieve all contracts with remaining payments due.

        Returns:
            List[Contract]: List of unpaid contracts.
        """
        return self.get(Contract.to_be_paid > 0)

    @permission_required(roles=[Department.ACCOUNTING, Department.SALES])
    def update(self, where_clause, **values):
        """
        Update contract(s) that match the given condition. Sales users can only update their own contracts.

        Args:
            where_clause: SQLAlchemy condition to locate contracts.
            **values: Fields to update.

        Returns:
            int: Number of records updated.

        Raises:
            PermissionError: If the sales user tries to modify a contract not assigned to them.
        """
        user = self.get_authenticated_user()
        if user.role == Department.SALES:
            accessed_contracts = self.get(where_clause)
            for contract in accessed_contracts:
                if contract.sales_contact_id != user.id:
                    raise PermissionError("Permission denied: not responsible for this contract.")
        return super().update(where_clause, **values)

    @permission_required(roles=[Department.ACCOUNTING, Department.SALES])
    def delete(self, where_clause):
        """
        Delete contract(s) that match the given condition. Sales users can only delete their own contracts.

        Args:
            where_clause: SQLAlchemy condition to locate contracts.

        Returns:
            int: Number of records deleted.

        Raises:
            PermissionError: If the sales user tries to delete a contract not assigned to them.
        """
        user = self.get_authenticated_user()
        if user.role == Department.SALES:
            accessed_contracts = self.get(where_clause)
            for contract in accessed_contracts:
                if contract.sales_contact_id != user.id:
                    raise PermissionError("Permission denied: not responsible for this contract.")
        return super().delete(where_clause)

    def resolve_cascade(self, contracts: List[Contract]) -> List[CascadeDetails]:
        """
        Resolve and return all cascading dependencies related to the given contracts.

        Args:
            contracts (List[Contract]): List of contract instances.

        Returns:
            List[CascadeDetails]: List of cascade-related dependencies (e.g., related events, clients).
        """
        return self.cascade_resolver.resolve_contracts_cascade(contracts=contracts)
