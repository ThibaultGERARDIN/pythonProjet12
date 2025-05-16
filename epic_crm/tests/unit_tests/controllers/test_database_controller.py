import pytest
from sqlalchemy import inspect, text
from controllers.database_controller import engine


def test_tables_are_created(setup_database):
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    # Liste des tables attendues dans la base
    expected_tables = {"users", "clients", "contracts", "events"}

    for table in expected_tables:
        assert table in tables, f"Table {table} is missing"


def test_database_connection():
    # Vérifie qu'une connexion peut être établie
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        assert result.scalar() == 1
