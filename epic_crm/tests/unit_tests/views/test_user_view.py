import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from epic_crm.views import user_view


@pytest.fixture
def runner():
    return CliRunner()


def test_create_user_cmd_success(runner):
    mock_user = MagicMock()
    mock_user.email = "user@example.com"
    mock_user.id = 1

    with patch("epic_crm.views.user_view.get_manager") as mock_get_manager:
        mock_manager = MagicMock()
        mock_manager.create.return_value = mock_user
        mock_session = MagicMock()
        mock_get_manager.return_value = (mock_manager, mock_session)

        result = runner.invoke(
            user_view.create_user_cmd, input="Jane\nDoe\nuser@example.com\npass123\npass123\nsales\n"
        )

        assert result.exit_code == 0
        assert "Utilisateur user@example.com créé (ID: 1)" in result.output
        mock_manager.create.assert_called_once()


def test_login_success(runner):
    token = "fake.jwt.token"
    with patch("epic_crm.views.user_view.authenticate_user", return_value=(True, token)), patch(
        "builtins.open", create=True
    ) as mock_open:

        result = runner.invoke(user_view.login, input="user@example.com\npassword\n")

        assert result.exit_code == 0
        assert "Connexion réussie" in result.output
        assert token in result.output
        mock_open.assert_called_once_with(".token", "w")


def test_login_failure(runner):
    with patch("epic_crm.views.user_view.authenticate_user", return_value=(False, "Identifiants invalides")):
        result = runner.invoke(user_view.login, input="user@example.com\nwrongpass\n")

        assert result.exit_code == 0
        assert "Identifiants invalides" in result.output


def test_logout_with_token_file(runner, tmp_path):
    token_path = tmp_path / ".token"
    token_path.write_text("fake-token")

    with patch("epic_crm.views.user_view.os.path.exists", return_value=True), patch(
        "epic_crm.views.user_view.os.remove"
    ) as mock_remove:

        result = runner.invoke(user_view.logout)

        assert "Déconnecté avec succès" in result.output
        mock_remove.assert_called_once()


def test_logout_without_token_file(runner):
    with patch("epic_crm.views.user_view.os.path.exists", return_value=False):
        result = runner.invoke(user_view.logout)
        assert "Aucun token trouvé." in result.output


def test_current_user_success(runner):
    mock_payload = {"email": "user@example.com", "role": "SALES"}

    with patch("epic_crm.views.user_view.get_current_user_token_payload", return_value=mock_payload):
        result = runner.invoke(user_view.current_user)
        assert "Connecté en tant que user@example.com (SALES)" in result.output


def test_current_user_no_token(runner):
    with patch("epic_crm.views.user_view.get_current_user_token_payload", side_effect=ValueError("Token manquant")):
        result = runner.invoke(user_view.current_user)
        assert "Token manquant" in result.output


def test_list_users_success(runner):
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.full_name = "John Doe"
    mock_user.email = "john@example.com"
    mock_user.role.name = "SUPPORT"

    with patch("epic_crm.views.user_view.get_manager") as mock_get_manager:
        mock_manager = MagicMock()
        mock_manager.get_all.return_value = [mock_user]
        mock_session = MagicMock()
        mock_get_manager.return_value = (mock_manager, mock_session)

        result = runner.invoke(user_view.list_users)
        assert "[1] John Doe - john@example.com (SUPPORT)" in result.output
