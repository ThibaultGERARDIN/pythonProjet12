import sqlalchemy
from sqlalchemy.orm import Session
from typing import List
from abc import ABC, abstractmethod

from controllers.authentication import retrieve_authenticated_user
from controllers.cascade_controller import CascadeDetails, CascadeResolver
from models.users import User


class BaseManager(ABC):
    """
    Abstract base class for all model managers.

    Provides a generic interface for CRUD operations (Create, Read, Update, Delete)
    on SQLAlchemy models, and handles authenticated user context and cascade logic.
    Subclasses must implement the `resolve_cascade` method.
    """

    def __init__(self, session: Session, model: type) -> None:
        """
        Initialize the manager with a database session and a model type.

        Args:
            session (Session): SQLAlchemy session instance.
            model (type): SQLAlchemy model class to manage.
        """
        self._session = session
        self._model = model
        self.cascade_resolver = CascadeResolver(session)

    def get_authenticated_user(self) -> User:
        """
        Retrieve the currently authenticated user from the database session.

        Returns:
            User: Authenticated user instance.

        Raises:
            PermissionError: If no authenticated user is found.
        """
        user = retrieve_authenticated_user(self._session)
        if not user:
            raise PermissionError("Aucun utilisateur authentifié trouvé.")
        return user

    def create(self, obj):
        """
        Persist a new object to the database.

        Args:
            obj: Instance of the managed model.

        Returns:
            obj: The same object after insertion.
        """
        self._session.add(obj)
        self._session.commit()

        return obj

    def get_all(self):
        """
        Retrieve all records of the managed model.

        Returns:
            List[model]: All records from the table.
        """
        request = sqlalchemy.select(self._model)
        return self._session.scalars(request).all()

    def get(self, where_clause):
        """
        Retrieve records matching a given condition.

        Args:
            where_clause: SQLAlchemy-compatible filter condition.

        Returns:
            List[model]: Matching records.
        """
        request = sqlalchemy.select(self._model).where(where_clause)
        return self._session.scalars(request).all()

    def update(self, where_clause, **values):
        """
        Update records matching a condition with new values.

        Args:
            where_clause: SQLAlchemy-compatible filter condition.
            **values: Fields and their new values.
        """
        self._session.execute(sqlalchemy.update(self._model).where(where_clause).values(**values))
        self._session.commit()

    def delete(self, where_clause):
        """
        Delete records that match a given condition.

        Args:
            where_clause: SQLAlchemy-compatible filter condition.
        """
        self._session.execute(sqlalchemy.delete(self._model).where(where_clause))
        self._session.commit()

    @abstractmethod
    def resolve_cascade(self, objects: List[object]) -> List[CascadeDetails]:
        """
        Abstract method that must be implemented by subclasses to describe
        cascade deletions for a given list of model instances.

        Args:
            objects (List[object]): Objects for which to resolve cascade impact.

        Returns:
            List[CascadeDetails]: A list of objects that would be affected.
        """
        pass
