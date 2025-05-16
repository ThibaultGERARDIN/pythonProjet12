import pytest
import sys
import os
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from models.base import Base
from controllers.user_controller import UserManager
from controllers import authentication


load_dotenv()


DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PWD = os.getenv("DATABASE_PWD")
SECRET_KEY = os.getenv("SECRET_KEY")

DATABASE_URL = f"mysql+pymysql://{DATABASE_USER}:{DATABASE_PWD}@localhost:3306/epic_crm_test"

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)


@pytest.fixture(scope="session")
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(autouse=True)
def patch_sessionlocal(monkeypatch, test_db_session):
    """
    Force tous les appels à SessionLocal() dans authentication.py
    à retourner la session de test.
    """
    monkeypatch.setattr(authentication, "SessionLocal", lambda: test_db_session)


@pytest.fixture
def token_file():
    payload = {
        "user_id": 2,
        "email": "sales@epic.com",
        "role": "SALES",
        "exp": datetime.now() + timedelta(hours=1),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    # Crée le fichier .token
    with open(".token", "w") as f:
        f.write(token)

    yield

    # Nettoyage
    if os.path.exists(".token"):
        os.remove(".token")


@pytest.fixture
def mock_auth_sales(monkeypatch):
    mock_data = {"user_id": 2, "email": "sales@test.com", "role": "SALES"}
    monkeypatch.setattr("controllers.permissions.get_current_user_token_payload", lambda: mock_data)
    monkeypatch.setattr("controllers.authentication.get_current_user_token_payload", lambda: mock_data)


@pytest.fixture
def mock_auth_support(monkeypatch):
    mock_data = {"user_id": 3, "email": "support@test.com", "role": "SUPPORT"}
    monkeypatch.setattr("controllers.permissions.get_current_user_token_payload", lambda: mock_data)
    monkeypatch.setattr("controllers.authentication.get_current_user_token_payload", lambda: mock_data)


@pytest.fixture
def mock_auth_accounting(monkeypatch):
    mock_data = {"user_id": 1, "email": "acc@test.com", "role": "ACCOUNTING"}
    monkeypatch.setattr("controllers.permissions.get_current_user_token_payload", lambda: mock_data)
    monkeypatch.setattr("controllers.authentication.get_current_user_token_payload", lambda: mock_data)


@pytest.fixture
def user_manager(test_db_session):
    return UserManager(session=test_db_session)


class DummyScalarResult:
    def __init__(self, data):
        self.data = data

    def all(self):
        return self.data

    def __iter__(self):
        return iter(self.data)


class DummySession:
    def __init__(self):
        self.data = []
        self.added = []
        self.updated = []
        self.deleted = []
        self.get_return_value = None
        self.scalar_return_value = None

    def add(self, obj):
        self.added.append(obj)
        self.data.append(obj)

    def commit(self):
        pass

    def scalars(self, stmt):
        return DummyScalarResult(self.data)

    def scalar(self, stmt):
        return getattr(self, "scalar_return_value", None)

    def execute(self, stmt):
        self.updated.append(stmt)

    def get(self, model, id_):
        if self.get_return_value is not None:
            return self.get_return_value
        for obj in self.data:
            if isinstance(obj, model) and getattr(obj, "id", None) == id_:
                return obj
        return None

    def close(self):
        pass


@pytest.fixture
def dummy_session():
    return DummySession()
