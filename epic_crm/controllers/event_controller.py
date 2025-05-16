from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from controllers.permissions import permission_required
from controllers.base_controller import BaseManager
from controllers.cascade_controller import CascadeDetails
from controllers import utils
from models.users import Department, User
from models.contracts import Contract
from models.events import Event


class EventsManager(BaseManager):
    """
    Manage the access to ``Event`` table.
    """

    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=Event)

    @permission_required([Department.SALES])
    def create(
        self,
        event_name: str,
        start_date=datetime,
        end_date=datetime,
        location=str,
        attendees=int,
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

        client_id = contract.client_id
        # Vérifier que le client appartient au sales actuel
        user = self.get_authenticated_user()
        if contract.sales_contact_id != user.id:
            raise PermissionError("Permission denied: not your contract.")

        return super().create(
            Event(
                event_name=event_name,
                start_date=start_date,
                end_date=end_date,
                location=location,
                attendees=attendees,
                notes=notes,
                contract_id=contract_id,
                support_contact_id=support_contact_id,
                client_id=client_id,
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
