import click
from controllers.database_controller import engine
from models.base import Base
from views.user_view import create_user_cmd, login, current_user, logout
from views.client_view import client
from views.contract_view import contract
from views.event_view import event
from views.admin_view import create_admin, reset_db, delete_users


@click.group()
def cli():
    """CLI pour le CRM d’Epic Events."""
    pass


cli.add_command(create_user_cmd, name="create-user")
cli.add_command(login)
cli.add_command(logout)
cli.add_command(current_user)
cli.add_command(client)
cli.add_command(contract)
cli.add_command(event)
cli.add_command(reset_db)
cli.add_command(delete_users)
cli.add_command(create_admin)


@cli.command()
def init_db():
    """Initialise la base de données."""
    Base.metadata.create_all(bind=engine)
    click.echo("Base de données MySQL initialisée avec succès.")


if __name__ == "__main__":
    cli()
