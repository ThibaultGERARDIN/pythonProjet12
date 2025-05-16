import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from epic_crm.views import client_view


@pytest.fixture
def runner():
    return CliRunner()


def test_create_client_success(runner):
    mock_client = MagicMock()
    mock_client.full_name = "Client Test"
    mock_client.id = 42

    with patch("epic_crm.views.client_view.get_manager") as mock_get_manager:
        mock_manager = MagicMock()
        mock_manager.create.return_value = mock_client
        mock_session = MagicMock()
        mock_get_manager.return_value = (mock_manager, mock_session)

        result = runner.invoke(
            client_view.create,
            input="Client Test\nclient@test.com\n0123456789\nTestCorp\n"
        )

        assert result.exit_code == 0
        assert "Client Client Test créé (ID: 42)" in result.output
        mock_manager.create.assert_called_once()


def test_create_client_failure(runner):
    with patch("epic_crm.views.client_view.get_manager") as mock_get_manager:
        mock_manager = MagicMock()
        mock_manager.create.side_effect = Exception("Erreur de création")
        mock_session = MagicMock()
        mock_get_manager.return_value = (mock_manager, mock_session)

        result = runner.invoke(
            client_view.create,
            input="Client Test\nclient@test.com\n0123456789\nTestCorp\n"
        )

        assert "Erreur de création" in result.output


def test_list_clients(runner):
    mock_client = MagicMock()
    mock_client.id = 1
    mock_client.full_name = "Alice"
    mock_client.email = "alice@test.com"
    mock_client.enterprise = "AliceCorp"

    with patch("epic_crm.views.client_view.get_manager") as mock_get_manager:
        mock_manager = MagicMock()
        mock_manager.get_all.return_value = [mock_client]
        mock_session = MagicMock()
        mock_get_manager.return_value = (mock_manager, mock_session)

        result = runner.invoke(client_view.list)
        assert "[1] Alice - alice@test.com (AliceCorp)" in result.output


def test_update_client_success(runner):
    with patch("epic_crm.views.client_view.get_manager") as mock_get_manager:
        mock_manager = MagicMock()
        mock_session = MagicMock()
        mock_get_manager.return_value = (mock_manager, mock_session)

        result = runner.invoke(
            client_view.update,
            input="1\nnew@example.com\n0612345678\nNewCorp\n"
        )

        assert result.exit_code == 0
        assert "Client 1 mis à jour avec succès." in result.output
        mock_manager.update.assert_called_once()


def test_update_client_failure(runner):
    with patch("epic_crm.views.client_view.get_manager") as mock_get_manager:
        mock_manager = MagicMock()
        mock_manager.update.side_effect = Exception("Erreur de mise à jour")
        mock_session = MagicMock()
        mock_get_manager.return_value = (mock_manager, mock_session)

        result = runner.invoke(
            client_view.update,
            input="1\nnew@example.com\n0612345678\nNewCorp\n"
        )

        assert "Erreur de mise à jour" in result.output


def test_delete_client_success(runner):
    with patch("epic_crm.views.client_view.get_manager") as mock_get_manager:
        mock_manager = MagicMock()
        mock_session = MagicMock()
        mock_get_manager.return_value = (mock_manager, mock_session)

        result = runner.invoke(client_view.delete, input="1\n")

        assert "Client 1 supprimé." in result.output
        mock_manager.delete.assert_called_once()
