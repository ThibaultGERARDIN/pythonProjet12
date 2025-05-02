import click
from controllers.client_controller import create_client, list_clients, update_client, delete_client
from controllers.authentication import get_current_user_token_payload


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
    user = get_current_user_token_payload()
    success, msg = create_client(full_name, email, phone, company_name, user["user_id"])
    click.echo(msg)


@client.command()
def list():
    clients = list_clients()
    for c in clients:
        click.echo(f"[{c.id}] {c.full_name} - {c.email} ({c.company_name})")


@client.command()
@click.option("--client-id", prompt="ID du client")
@click.option("--email", default=None)
@click.option("--phone", default=None)
@click.option("--company-name", default=None)
def update(client_id, email, phone, company_name):
    success, msg = update_client(int(client_id), email=email, phone=phone, company_name=company_name)
    click.echo(msg)


@client.command()
@click.option("--client-id", prompt="ID du client")
def delete(client_id):
    success, msg = delete_client(int(client_id))
    click.echo(msg)
