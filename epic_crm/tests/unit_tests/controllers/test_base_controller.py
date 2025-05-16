from controllers.base_controller import BaseManager
from sqlalchemy import Column, Integer
from models.base import Base


class FakeModel(Base):
    __tablename__ = "fake"
    id = Column(Integer, primary_key=True)


class FakeManager(BaseManager):
    def resolve_cascade(self, objects):
        return []


def test_create_object(dummy_session):
    manager = FakeManager(session=dummy_session, model=FakeModel)
    obj = FakeModel(id=1)
    result = manager.create(obj)
    assert result in dummy_session.data
    assert obj in dummy_session.added


def test_get_all(dummy_session):
    obj = FakeModel(id=1)
    dummy_session.data = [obj]
    manager = FakeManager(session=dummy_session, model=FakeModel)
    result = manager.get_all()
    assert result == [obj]


def test_get_with_clause(dummy_session):
    obj = FakeModel(id=2)
    dummy_session.data = [obj]
    manager = FakeManager(session=dummy_session, model=FakeModel)
    result = manager.get(FakeModel.id == 2)
    assert result == [obj]


def test_update_object(dummy_session):
    manager = FakeManager(session=dummy_session, model=FakeModel)
    manager.update(FakeModel.id == 1, some_field="value")
    assert len(dummy_session.updated) == 1


def test_delete_object(dummy_session):
    manager = FakeManager(session=dummy_session, model=FakeModel)
    manager.delete(FakeModel.id == 1)
    assert len(dummy_session.updated) == 1
