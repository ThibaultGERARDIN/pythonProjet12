import sqlalchemy
from sqlalchemy.orm import Session
from typing import List
from abc import ABC, abstractmethod

from controllers.authentication import retrieve_authenticated_user
from controllers.cascade_controller import CascadeDetails, CascadeResolver
from models.users import User


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
        user = retrieve_authenticated_user(self._session)
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
