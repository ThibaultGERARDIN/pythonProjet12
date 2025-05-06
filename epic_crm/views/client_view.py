import click
from controllers.crud_controller import ClientsManager
from controllers.utils import get_manager
from controllers.authentication import get_current_user_token_payload
from models.clients import Client


@click.group()
def client():
    """Commandes de gestion des clients."""
    pass


@client.command()
@click.option("--full-name", prompt=True)
@click.option("--email", prompt=True)
@click.option("--phone", prompt=True)
@click.option("--company-name", prompt=True)
def create(full_name, email, phone, company_name):
    manager, session = get_manager(ClientsManager)
    try:
        user_id = get_current_user_token_payload()["user_id"]
        client = manager.create(email=email, full_name=full_name, phone=phone, enterprise=company_name)
        click.secho(f"Client {client.full_name} créé (ID: {client.id})", fg="green")
    except Exception as e:
        click.secho(str(e), fg="red")
    finally:
        session.close()


@client.command()
def list():
    manager, session = get_manager(ClientsManager)
    try:
        clients = manager.get_all()
        for c in clients:
            click.echo(f"[{c.id}] {c.full_name} - {c.email} ({c.enterprise})")
    finally:
        session.close()


@client.command()
@click.option("--client-id", prompt="ID du client")
@click.option("--email", default=None)
@click.option("--phone", default=None)
@click.option("--company-name", default=None)
def update(client_id, email, phone, company_name):
    manager, session = get_manager(ClientsManager)
    try:
        manager.update(Client.id == int(client_id), email=email, phone=phone, enterprise=company_name)
        click.secho(f"Client {client_id} mis à jour avec succès.", fg="green")
    except Exception as e:
        click.secho(str(e), fg="red")
    finally:
        session.close()


@client.command()
@click.option("--client-id", prompt="ID du client")
def delete(client_id):
    manager, session = get_manager(ClientsManager)
    try:
        manager.delete(Client.id == int(client_id))
        click.secho(f"Client {client_id} supprimé.", fg="yellow")
    finally:
        session.close()
