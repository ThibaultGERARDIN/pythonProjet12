import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from epic_crm.views import contract_view


@pytest.fixture
def runner():
    return CliRunner()


def test_create_contract_success(runner):
    mock_contract = MagicMock()
    mock_contract.id = 99

    with patch("epic_crm.views.contract_view.get_manager") as mock_get_manager:
        mock_manager = MagicMock()
        mock_manager.create.return_value = mock_contract
        mock_session = MagicMock()
        mock_get_manager.return_value = (mock_manager, mock_session)

        result = runner.invoke(contract_view.create, input="1\n1000.0\n500.0\nTrue\n")

        assert result.exit_code == 0
        assert "Contrat créé avec ID : 99" in result.output
        mock_manager.create.assert_called_once_with(1, 1000.0, 500.0, True)


def test_create_contract_failure(runner):
    with patch("epic_crm.views.contract_view.get_manager") as mock_get_manager:
        mock_manager = MagicMock()
        mock_manager.create.side_effect = Exception("Erreur création")
        mock_session = MagicMock()
        mock_get_manager.return_value = (mock_manager, mock_session)

        result = runner.invoke(contract_view.create, input="1\n1000.0\n500.0\nTrue\n")

        assert "Erreur création" in result.output


def test_list_contracts(runner):
    mock_contract = MagicMock()
    mock_contract.id = 5
    mock_contract.client_id = 1
    mock_contract.total_amount = 2000
    mock_contract.is_signed = True

    with patch("epic_crm.views.contract_view.get_manager") as mock_get_manager:
        mock_manager = MagicMock()
        mock_manager.get_all.return_value = [mock_contract]
        mock_session = MagicMock()
        mock_get_manager.return_value = (mock_manager, mock_session)

        result = runner.invoke(contract_view.list)

        assert "[5] Client #1 - Total: 2000€ - Signé: Oui" in result.output


def test_update_contract_success(runner):
    with patch("epic_crm.views.contract_view.get_manager") as mock_get_manager:
        mock_manager = MagicMock()
        mock_session = MagicMock()
        mock_get_manager.return_value = (mock_manager, mock_session)

        result = runner.invoke(contract_view.update, input="3\n1500.0\n750.0\nTrue\n")

        assert "Contrat mis à jour." in result.output
        mock_manager.update.assert_called_once()


def test_update_contract_failure(runner):
    with patch("epic_crm.views.contract_view.get_manager") as mock_get_manager:
        mock_manager = MagicMock()
        mock_manager.update.side_effect = Exception("Erreur update")
        mock_session = MagicMock()
        mock_get_manager.return_value = (mock_manager, mock_session)

        result = runner.invoke(contract_view.update, input="3\n1500.0\n750.0\nTrue\n")

        assert "Erreur update" in result.output


def test_delete_contract_success(runner):
    with patch("epic_crm.views.contract_view.get_manager") as mock_get_manager:
        mock_manager = MagicMock()
        mock_session = MagicMock()
        mock_get_manager.return_value = (mock_manager, mock_session)

        result = runner.invoke(contract_view.delete, input="5\n")

        assert "Contrat 5 supprimé." in result.output
        mock_manager.delete.assert_called_once()
