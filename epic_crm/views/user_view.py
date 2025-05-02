import click
from controllers.user_controller import create_user, authenticate_user
from controllers.authentication import get_current_user_token_payload


@click.command()
@click.option("--firstname", prompt="Prénom")
@click.option("--lastname", prompt="Nom")
@click.option("--email", prompt="Email")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
@click.option("--role", type=click.Choice(["gestion", "commercial", "support"]), prompt="Rôle")
def create_user_cmd(firstname, lastname, email, password, role):
    """Créer un utilisateur (via CLI)."""
    success, message = create_user(firstname, lastname, email, password, role)
    if success:
        click.echo(f"{message}")
    else:
        click.echo(f"{message}")


@click.command()
@click.option("--email", prompt="Email")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--save-token", is_flag=True, help="Sauvegarder le token localement")
def login(email, password, save_token):
    """Connexion utilisateur avec token JWT."""
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
def current_user():
    """Affiche l'utilisateur connecté."""
    try:
        user = get_current_user_token_payload()
        click.echo(f"Connecté en tant que {user['email']} ({user['role']})")
    except ValueError as e:
        click.secho(f"{str(e)}", fg="red")
