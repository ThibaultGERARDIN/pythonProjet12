import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from epic_crm.views import event_view


@pytest.fixture
def runner():
    return CliRunner()


def test_create_event_success(runner):
    mock_event = MagicMock()
    mock_event.id = 10

    with patch("epic_crm.views.event_view.get_manager") as mock_get_manager:
        mock_manager = MagicMock()
        mock_manager.create.return_value = mock_event
        mock_session = MagicMock()
        mock_get_manager.return_value = (mock_manager, mock_session)

        result = runner.invoke(
            event_view.create, input="Kickoff\n2025-09-01 10:00\n2025-09-01 12:00\nParis\n20\nDébut projet\n1\n2\n"
        )

        assert result.exit_code == 0
        assert "Événement créé (ID: 10)" in result.output
        mock_manager.create.assert_called_once()


def test_create_event_failure(runner):
    with patch("epic_crm.views.event_view.get_manager") as mock_get_manager:
        mock_manager = MagicMock()
        mock_manager.create.side_effect = Exception("Erreur création")
        mock_session = MagicMock()
        mock_get_manager.return_value = (mock_manager, mock_session)

        result = runner.invoke(
            event_view.create, input="Kickoff\n2025-09-01 10:00\n2025-09-01 12:00\nParis\n20\nDébut projet\n1\n2\n"
        )

        assert "Erreur création" in result.output


def test_list_events(runner):
    mock_event = MagicMock()
    mock_event.id = 1
    mock_event.event_name = "Réunion"
    mock_event.start_date = "2025-09-01"
    mock_event.location = "Nice"
    mock_event.contract_id = 2
    mock_event.support_contact_id = 3

    with patch("epic_crm.views.event_view.get_manager") as mock_get_manager:
        mock_manager = MagicMock()
        mock_manager.get_all.return_value = [mock_event]
        mock_session = MagicMock()
        mock_get_manager.return_value = (mock_manager, mock_session)

        result = runner.invoke(event_view.list)

        assert "[1] Réunion - 2025-09-01 à Nice (Contrat #2, Support: 3)" in result.output


def test_list_unassigned_events(runner):
    mock_event = MagicMock()
    mock_event.id = 7
    mock_event.event_name = "Sans Support"
    mock_event.start_date = "2025-12-01"
    mock_event.location = "Lyon"

    with patch("epic_crm.views.event_view.get_manager") as mock_get_manager:
        mock_manager = MagicMock()
        mock_manager.get_unassigned_support_events.return_value = [mock_event]
        mock_session = MagicMock()
        mock_get_manager.return_value = (mock_manager, mock_session)

        result = runner.invoke(event_view.list_unassigned)

        assert "[7] Sans Support - 2025-12-01 à Lyon" in result.output


def test_list_my_events(runner):
    mock_event = MagicMock()
    mock_event.id = 4
    mock_event.event_name = "Support Event"
    mock_event.start_date = "2025-10-10"
    mock_event.location = "Bordeaux"

    with patch("epic_crm.views.event_view.get_manager") as mock_get_manager:
        mock_manager = MagicMock()
        mock_manager.get_my_events.return_value = [mock_event]
        mock_session = MagicMock()
        mock_get_manager.return_value = (mock_manager, mock_session)

        result = runner.invoke(event_view.list_my_events)

        assert "[4] Support Event - 2025-10-10 à Bordeaux" in result.output


def test_update_event_success():
    runner = CliRunner()
    with patch("epic_crm.views.event_view.get_manager") as mock_get_manager:
        mock_manager = MagicMock()
        mock_session = MagicMock()
        mock_get_manager.return_value = (mock_manager, mock_session)

        result = runner.invoke(
            event_view.update,
            [
                "--event-id",
                "5",
                "--location",
                "Marseille",
                "--attendees",
                "100",
                "--notes",
                "Nouvelles notes",
                "--support-id",
                "3",
            ],
        )

        assert result.exit_code == 0
        assert "Événement mis à jour avec succès." in result.output
        mock_manager.update.assert_called_once()


def test_update_event_failure():
    runner = CliRunner()
    with patch("epic_crm.views.event_view.get_manager") as mock_get_manager:
        mock_manager = MagicMock()
        mock_manager.update.side_effect = Exception("Erreur update")
        mock_session = MagicMock()
        mock_get_manager.return_value = (mock_manager, mock_session)

        result = runner.invoke(
            event_view.update,
            [
                "--event-id",
                "5",
                "--location",
                "Marseille",
                "--attendees",
                "100",
                "--notes",
                "Nouvelles notes",
                "--support-id",
                "3",
            ],
        )
        assert "Erreur update" in result.output


def test_delete_event_success(runner):
    with patch("epic_crm.views.event_view.get_manager") as mock_get_manager:
        mock_manager = MagicMock()
        mock_session = MagicMock()
        mock_get_manager.return_value = (mock_manager, mock_session)

        result = runner.invoke(event_view.delete, input="8\n")

        assert "Événement 8 supprimé." in result.output
        mock_manager.delete.assert_called_once()


def test_delete_event_failure(runner):
    with patch("epic_crm.views.event_view.get_manager") as mock_get_manager:
        mock_manager = MagicMock()
        mock_manager.delete.side_effect = Exception("Suppression échouée")
        mock_session = MagicMock()
        mock_get_manager.return_value = (mock_manager, mock_session)

        result = runner.invoke(event_view.delete, input="8\n")

        assert "Suppression échouée" in result.output
