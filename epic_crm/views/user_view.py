import click
import os
from controllers.authentication import get_current_user_token_payload, authenticate_user
from controllers.user_controller import UserManager
from controllers.utils import get_manager
from models.users import Department


@click.command()
@click.option("--firstname", prompt="Prénom")
@click.option("--lastname", prompt="Nom")
@click.option("--email", prompt="Email")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
@click.option("--role", type=click.Choice(["accounting", "sales", "support"]), prompt="Rôle")
def create_user_cmd(firstname, lastname, email, password, role):
    """
    Create a new user via the CLI.

    Prompts for the user's first name, last name, email, password, and role.
    Only available to authorized users (e.g. ACCOUNTING).

    Raises:
        Exception: If the creation fails or access is denied.
    """
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
    """
    Authenticate a user with email and password.

    Generates a JWT token upon success. Optionally saves the token
    to a `.token` file for subsequent use.

    Raises:
        Exception: If authentication fails.
    """

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
    """
    Log out the current user by deleting the local JWT token file.

    If the `.token` file does not exist, notifies the user.
    """

    if os.path.exists(".token"):
        os.remove(".token")
        click.secho("Déconnecté avec succès. Token supprimé.", fg="green")
    else:
        click.secho("Aucun token trouvé.", fg="yellow")


@click.command()
def current_user():
    """
    Display the currently authenticated user.

    Parses the JWT token and prints the associated user ID and role.

    Raises:
        ValueError: If no valid token is found.
    """
    try:
        user = get_current_user_token_payload()
        click.echo(f"Connecté en tant que {user['email']} ({user['role']})")
    except ValueError as e:
        click.secho(f"{str(e)}", fg="red")


@click.command(name="list-users")
def list_users():
    """
    List all users registered in the system.

    Accessible to ACCOUNTING users only. Displays ID, name, email,
    and department role for each user.

    Raises:
        Exception: If the request fails or permission is denied.
    """
    manager, session = get_manager(UserManager)
    try:
        users = manager.get_all()
        for u in users:
            click.echo(f"[{u.id}] {u.full_name} - {u.email} ({u.role.name})")
    except Exception as e:
        click.secho(str(e), fg="red")
    finally:
        session.close()
