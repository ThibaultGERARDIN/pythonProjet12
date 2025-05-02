import click
from controllers.contract_controller import create_contract, list_contracts, update_contract, delete_contract
from controllers.authentication import get_current_user_token_payload


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
    user = get_current_user_token_payload()
    success, msg = create_contract(
        client_id=client_id,
        sales_contact_id=user["user_id"],
        amount_total=amount_total,
        amount_remaining=amount_remaining,
        is_signed=is_signed,
    )
    click.echo(msg)


@contract.command()
def list():
    contracts = list_contracts()
    for c in contracts:
        signed = "Oui" if c.is_signed else "Non"
        click.echo(f"[{c.id}] Client #{c.client_id} - Total: {c.amount_total}€ - Signé: {signed}")


@contract.command()
@click.option("--contract-id", prompt="ID du contrat")
@click.option("--amount-total", type=float, default=None)
@click.option("--amount-remaining", type=float, default=None)
@click.option("--is-signed", type=bool, default=None)
def update(contract_id, amount_total, amount_remaining, is_signed):
    success, msg = update_contract(
        int(contract_id), amount_total=amount_total, amount_remaining=amount_remaining, is_signed=is_signed
    )
    click.echo(msg)


@contract.command()
@click.option("--contract-id", prompt="ID du contrat")
def delete(contract_id):
    success, msg = delete_contract(int(contract_id))
    click.echo(msg)
