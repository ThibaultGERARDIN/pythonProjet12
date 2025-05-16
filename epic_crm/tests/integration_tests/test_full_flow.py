import os
import pytest
from controllers import permissions
from controllers.user_controller import UserManager
from controllers.authentication import authenticate_user
from controllers.client_controller import ClientsManager
from controllers.contract_controller import ContractsManager
from controllers.event_controller import EventsManager
from models.users import Department
from models.clients import Client
from models.contracts import Contract
from models.events import Event

# -- Chargement des variables d'environnement
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")


@pytest.fixture
def patch_permission_sessionlocal(monkeypatch, test_db_session):
    """
    Force tous les appels à SessionLocal() dans permissions.py
    à retourner la session de test.
    """
    monkeypatch.setattr(permissions, "SessionLocal", lambda: test_db_session)


@pytest.fixture
def token_path(tmp_path):
    """
    Crée un fichier temporaire .token utilisé pour l'authentification.
    """
    return tmp_path / ".token"


def write_token(token: str, token_path):
    with open(token_path, "w") as f:
        f.write(token)
    # Force controllers à lire le bon fichier
    os.replace(token_path, ".token")


def test_full_flow(test_db_session, setup_database, patch_permission_sessionlocal, token_path):
    user_manager = UserManager(session=test_db_session)

    # --- Étape 1 : Créer un utilisateur ACCOUNTING (admin) et s'authentifier ---
    user_manager._create_admin_raw(
        email="admin_test@test.com",
        firstname="TEST",
        lastname="ADMIN",
        password="testadmin",
    )
    test_db_session.flush()
    test_db_session.commit()

    success, token = authenticate_user("admin_test@test.com", "testadmin")
    assert success is True
    write_token(token, token_path)

    # --- Étape 2 : Créer un utilisateur SALES et un SUPPORT ---
    sales_user = user_manager.create(
        email="sales_flow@test.com",
        firstname="Flow",
        lastname="Sales",
        password="testpass",
        role=Department.SALES,
    )

    support_user = user_manager.create(
        email="support_flow@test.com",
        firstname="Flow",
        lastname="Support",
        password="supportpass",
        role=Department.SUPPORT,
    )

    # --- Étape 3 : S’authentifier en tant que SALES ---
    success, token = authenticate_user("sales_flow@test.com", "testpass")
    assert success is True
    write_token(token, token_path)

    # --- Étape 4 : Créer un client ---
    client_manager = ClientsManager(test_db_session)
    client = client_manager.create(
        email="client_flow@test.com",
        full_name="Client Flow",
        phone="0606060606",
        enterprise="FlowCorp",
    )

    assert isinstance(client, Client)
    assert client.sales_contact_id == sales_user.id

    # --- Étape 4bis : Vérification de get_my_clients ---
    my_clients = client_manager.get_my_clients()
    assert isinstance(my_clients[0], Client)
    assert my_clients[0].id == client.id

    # --- Étape 5 : Créer un contrat ---
    contract_manager = ContractsManager(test_db_session)
    contract = contract_manager.create(
        client_id=client.id,
        total_amount=5000,
        to_be_paid=2500,
        is_signed=True,
    )

    assert isinstance(contract, Contract)

    # --- Étape 6 : Créer un événement ---
    event_manager = EventsManager(test_db_session)
    event = event_manager.create(
        event_name="Kickoff Flow",
        contract_id=contract.id,
        support_contact_id=support_user.id,
        attendees=15,
        start_date="2025-09-01",
        end_date="2025-09-02",
        location="Nice",
        notes="Réunion initiale du projet",
    )

    assert isinstance(event, Event)

    # --- Étape 7 : Login en tant que support_user et vérification de get_my_events ---
    success, token = authenticate_user("support_flow@test.com", "supportpass")
    assert success is True
    write_token(token, token_path)

    my_events = event_manager.get_my_events()
    assert isinstance(my_events[0], Event)
    assert my_events[0].id == event.id

    # --- Étape 8 : Tentative interdite : support essaye de créer un client ---
    with pytest.raises(PermissionError):
        ClientsManager(test_db_session).create(
            email="hack_attempt@test.com",
            full_name="Hacker",
            phone="0999999999",
            enterprise="HackCorp",
        )


