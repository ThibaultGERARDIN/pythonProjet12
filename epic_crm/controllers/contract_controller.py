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
    Manage the access to ``Contract`` table.
    """

    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=Contract)

    @permission_required(roles=[Department.ACCOUNTING, Department.SALES])
    def create(self, client_id: int, total_amount: float, to_be_paid: int, is_signed: bool):
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
