import click
from controllers.client_controller import ClientsManager
from controllers.utils import get_manager
from models.clients import Client


@click.group()
def client():
    """
    Client management command group.

    This command group contains subcommands to manage clients, including
    creation, listing, updating, and deletion operations.
    """
    pass


@client.command()
@click.option("--full-name", prompt=True)
@click.option("--email", prompt=True)
@click.option("--phone", prompt=True)
@click.option("--company-name", prompt=True)
def create(full_name, email, phone, company_name):
    """
    Create a new client.

    Prompts the user to enter client information such as full name, email,
    phone number, and company name. The client will be assigned to the
    currently authenticated sales user.

    Raises:
        Exception: If client creation fails (e.g., validation or permission issues).
    """
    manager, session = get_manager(ClientsManager)
    try:
        client = manager.create(email=email, full_name=full_name, phone=phone, enterprise=company_name)
        click.secho(f"Client {client.full_name} créé (ID: {client.id})", fg="green")
    except Exception as e:
        click.secho(str(e), fg="red")
    finally:
        session.close()


@client.command()
def list():
    """
    List all clients.

    Displays a summary of all clients registered in the system,
    including their ID, name, email, and associated company.
    """
    manager, session = get_manager(ClientsManager)
    try:
        clients = manager.get_all()
        for c in clients:
            click.echo(f"[{c.id}] {c.full_name} - {c.email} ({c.enterprise})")
    finally:
        session.close()


@client.command(name="list-my")
def get_my_clients():
    """
    Liste les clients assignés à l'utilisateur connecté (Sales uniquement).
    """
    manager, session = get_manager(ClientsManager)
    try:
        clients = manager.get_my_clients()
        if not clients:
            click.secho("Aucun client assigné.", fg="yellow")
        for c in clients:
            click.echo(f"[{c.id}] {c.full_name} - {c.enterprise} ({c.email})")
    except Exception as e:
        click.secho(str(e), fg="red")
    finally:
        session.close()


@client.command(name="filter-by-name")
@click.option("--name", prompt="Nom ou partie du nom à rechercher")
def filter_by_name(name):
    """
    Recherche les clients dont le nom contient la chaîne fournie.
    """
    manager, session = get_manager(ClientsManager)
    try:
        results = manager.filter_by_name(name)
        if not results:
            click.secho("Aucun client correspondant.", fg="yellow")
        for c in results:
            click.echo(f"[{c.id}] {c.full_name} - {c.enterprise} ({c.email})")
    except Exception as e:
        click.secho(str(e), fg="red")
    finally:
        session.close()


@client.command()
@click.option("--client-id", prompt="ID du client")
@click.option("--email", default=None)
@click.option("--phone", default=None)
@click.option("--company-name", default=None)
def update(client_id, email, phone, company_name):
    """
    Update a client's information.

    Allows updating selected fields (email, phone, or company name) for a given client.
    Only the sales user responsible for the client is authorized to perform the update.

    Args:
        client_id (int): The ID of the client to update.

    Raises:
        Exception: If the update fails due to permissions or invalid input.
    """
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
    """
    Delete a client.

    Removes the client with the specified ID from the system. This operation
    may trigger a cascade deletion of related data, depending on database constraints.

    Args:
        client_id (int): The ID of the client to delete.
    """
    manager, session = get_manager(ClientsManager)
    try:
        manager.delete(Client.id == int(client_id))
        click.secho(f"Client {client_id} supprimé.", fg="yellow")
    finally:
        session.close()
