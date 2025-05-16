import click
from controllers.contract_controller import ContractsManager
from controllers.utils import get_manager
from models.contracts import Contract


@click.group()
def contract():
    """Commandes de gestion des contrats."""
    pass


@contract.command()
@click.option("--client-id", prompt=True, type=int)
@click.option("--amount-total", prompt=True, type=float)
@click.option("--amount-remaining", prompt=True, type=float)
@click.option("--is-signed", type=bool, prompt="Contrat signé ? (True/False)")
def create(client_id, amount_total, amount_remaining, is_signed):
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
    manager, session = get_manager(ContractsManager)
    try:
        manager.delete(Contract.id == int(contract_id))
        click.secho(f"Contrat {contract_id} supprimé.", fg="yellow")
    finally:
        session.close()
