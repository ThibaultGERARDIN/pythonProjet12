import click
import os
from controllers.authentication import get_current_user_token_payload
from controllers.crud_controller import UserManager
from controllers.utils import get_manager
from models.users import Department


@click.command()
@click.option("--firstname", prompt="Prénom")
@click.option("--lastname", prompt="Nom")
@click.option("--email", prompt="Email")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
@click.option("--role", type=click.Choice(["accounting", "sales", "support"]), prompt="Rôle")
def create_user_cmd(firstname, lastname, email, password, role):
    """Créer un utilisateur (via CLI)."""
    manager, session = get_manager(UserManager)
    try:
        role_enum = Department[role.upper()]
        user = manager.create(firstname, lastname, email, password, role_enum)
        click.secho(f"Utilisateur {user.email} créé (ID: {user.id})", fg="green")
    except Exception as e:
        click.secho(str(e), fg="red")
    finally:
        session.close()


@click.command()
@click.option("--email", prompt="Email")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--save-token/--no-save-token", default=True, help="Sauvegarder le token dans .token (activé par défaut)")
def login(email, password, save_token):
    from controllers.authentication import authenticate_user

    success, token_or_msg = authenticate_user(email, password)
    if success:
        click.secho("Connexion réussie. Token JWT généré.", fg="green")
        click.echo(token_or_msg)
        if save_token:
            with open(".token", "w") as f:
                f.write(token_or_msg)
            click.secho("Token sauvegardé dans .token", fg="yellow")
    else:
        click.secho(f"{token_or_msg}", fg="red")


@click.command()
def logout():
    """Supprime le fichier de token JWT local."""

    if os.path.exists(".token"):
        os.remove(".token")
        click.secho("Déconnecté avec succès. Token supprimé.", fg="green")
    else:
        click.secho("Aucun token trouvé.", fg="yellow")


@click.command()
def current_user():
    """Affiche l'utilisateur connecté."""
    try:
        user = get_current_user_token_payload()
        click.echo(f"Connecté en tant que {user['email']} ({user['role']})")
    except ValueError as e:
        click.secho(f"{str(e)}", fg="red")
