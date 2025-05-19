import click
from controllers.contract_controller import ContractsManager
from controllers.utils import get_manager
from models.contracts import Contract


@click.group()
def contract():
    """
    Contract management command group.

    This group provides subcommands to manage client contracts, including
    creation, listing, updating, and deletion operations.
    """
    pass


@contract.command()
@click.option("--client-id", prompt=True, type=int)
@click.option("--amount-total", prompt=True, type=float)
@click.option("--amount-remaining", prompt=True, type=float)
@click.option("--is-signed", type=bool, prompt="Contrat signé ? (True/False)")
def create(client_id, amount_total, amount_remaining, is_signed):
    """
    Create a new contract for a client.

    Requires client ID and contract details such as total amount, remaining
    amount, and signature status. Only authorized users can create contracts
    for their assigned clients.

    Raises:
        Exception: If the client is not found or not assigned to the current user.
    """
    manager, session = get_manager(ContractsManager)
    try:
        contract = manager.create(client_id, amount_total, amount_remaining, is_signed)
        click.secho(f"Contrat créé avec ID : {contract.id}", fg="green")
    except Exception as e:
        click.secho(str(e), fg="red")
    finally:
        session.close()


@contract.command()
def list():
    """
    List all contracts in the system.

    Displays contract ID, client ID, total amount, and signature status
    for each contract accessible to the authenticated user.
    """
    manager, session = get_manager(ContractsManager)
    try:
        contracts = manager.get_all()
        for c in contracts:
            click.echo(
                f"[{c.id}] Client #{c.client_id} - Total: {c.total_amount}€ - Signé: {'Oui' if c.is_signed else 'Non'}"
            )
    finally:
        session.close()


@contract.command()
@click.option("--contract-id", prompt="ID du contrat")
@click.option("--amount-total", type=float, default=None)
@click.option("--amount-remaining", type=float, default=None)
@click.option("--is-signed", type=bool, default=None)
def update(contract_id, amount_total, amount_remaining, is_signed):
    """
    Update a contract's details.

    Allows modifying the total amount, remaining balance, and signature status.
    Sales users can only update contracts they are responsible for.

    Args:
        contract_id (int): ID of the contract to be updated.

    Raises:
        Exception: If the update is unauthorized or fails.
    """
    manager, session = get_manager(ContractsManager)
    try:
        manager.update(
            Contract.id == int(contract_id), total_amount=amount_total, to_be_paid=amount_remaining, is_signed=is_signed
        )
        click.secho("Contrat mis à jour.", fg="green")
    except Exception as e:
        click.secho(str(e), fg="red")
    finally:
        session.close()


@contract.command()
@click.option("--contract-id", prompt="ID du contrat")
def delete(contract_id):
    """
    Delete a contract.

    Removes the specified contract if the authenticated user has permission.
    Sales users may only delete contracts they own.

    Args:
        contract_id (int): ID of the contract to delete.
    """
    manager, session = get_manager(ContractsManager)
    try:
        manager.delete(Contract.id == int(contract_id))
        click.secho(f"Contrat {contract_id} supprimé.", fg="yellow")
    finally:
        session.close()
