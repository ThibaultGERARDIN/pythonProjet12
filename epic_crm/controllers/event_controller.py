from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from controllers.permissions import permission_required
from controllers.base_controller import BaseManager
from controllers.cascade_controller import CascadeDetails
from controllers import utils
from models.users import Department, User
from models.contracts import Contract
from models.events import Event


class EventsManager(BaseManager):
    """
    Manage the access to the ``Event`` table and implement business logic
    specific to event creation, update, and deletion based on user roles.
    """

    def __init__(self, session: Session) -> None:
        """
        Initialize the EventsManager with a SQLAlchemy session.

        Args:
            session (Session): SQLAlchemy session object.
        """
        super().__init__(session=session, model=Event)

    @permission_required([Department.SALES])
    def create(
        self,
        event_name: str,
        start_date: datetime,
        end_date: datetime,
        location: str,
        attendees: int,
        notes: str,
        contract_id: int,
        support_contact_id: Optional[int] = None,
    ) -> Event:
        """
        Create a new event. Only sales users are authorized.

        Validates that:
        - The contract exists and is signed.
        - The current user is the contract's sales contact.
        - If a support contact is provided, their role must be SUPPORT.

        Args:
            event_name (str): Name of the event.
            start_date (datetime): Event start date.
            end_date (datetime): Event end date.
            location (str): Location of the event.
            attendees (int): Number of attendees.
            notes (str): Optional notes.
            contract_id (int): Associated contract ID.
            support_contact_id (Optional[int]): Assigned support user ID.

        Returns:
            Event: The created event instance.

        Raises:
            ValueError: If contract or support user is invalid.
            PermissionError: If the contract is not assigned to the current user.
        """

        if support_contact_id is not None:
            support_user = self._session.get(User, support_contact_id)
            if not support_user:
                raise ValueError("Support user not found.")
            utils.check_user_role(support_user, Department.SUPPORT)

        contract = self._session.get(Contract, contract_id)
        if not contract or not contract.is_signed:
            raise ValueError("Contract must exist and be signed.")

        client_id = contract.client_id

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
        """
        Retrieve a list of events matching a specific condition.

        Args:
            where_clause: SQLAlchemy where clause for filtering.

        Returns:
            List[Event]: A list of matching event instances.
        """
        return super().get(where_clause)

    @permission_required(roles=Department)
    def get_all(self) -> List[Event]:
        """
        Retrieve all events in the system.

        Returns:
            List[Event]: All event records.
        """
        return super().get_all()

    @permission_required([Department.SUPPORT])
    def get_my_events(self) -> List[Event]:
        """
        Retrieve all events assigned to the currently authenticated support user.

        Returns:
            List[Event]: Events where the current user is the support contact.
        """
        user = self.get_authenticated_user()
        return self.get(Event.support_contact_id == user.id)

    def get_unassigned_support_events(self) -> List[Event]:
        """
        Retrieve all events that currently have no support contact assigned.

        Returns:
            List[Event]: Events with `support_contact_id` set to None.
        """
        return self.get(Event.support_contact_id is None)

    @permission_required([Department.ACCOUNTING, Department.SUPPORT])
    def update(self, where_clause, **values):
        """
        Update event attributes based on filtering criteria.

        Restrictions:
        - SUPPORT users may only update events they are assigned to.
        - If `support_contact_id` is provided, it must reference a SUPPORT user.

        Args:
            where_clause: SQLAlchemy where clause to match events.
            **values: Fields to update.

        Returns:
            None

        Raises:
            PermissionError: If SUPPORT user tries to update an event not assigned to them.
            ValueError: If new support contact is invalid.
        """

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
        """
        Delete one or more events based on a filter condition.

        Restrictions:
        - SUPPORT users may only delete events they are assigned to.

        Args:
            where_clause: SQLAlchemy where clause to filter deletions.

        Returns:
            None

        Raises:
            PermissionError: If SUPPORT user tries to delete events not assigned to them.
        """

        user = self.get_authenticated_user()
        accessed_objects = self.get(where_clause)

        # check that support employee own the accessed events
        if user.role == Department.SUPPORT:
            for event in accessed_objects:
                if event.support_contact_id != user.id:
                    raise PermissionError(f"Permission denied. Not authorized to update event {event.id}")

        return super().delete(where_clause)

    def resolve_cascade(self, events: List[Event]) -> List[CascadeDetails]:
        """
        Build and return cascade details for a list of events.

        Args:
            events (List[Event]): List of event instances.

        Returns:
            List[CascadeDetails]: A list containing cascade detail objects for the given events.
        """
        return [CascadeDetails(title="EVENTS", headers=Event.HEADERS, objects=events)]
