import click
from controllers.user_controller import UserManager
from controllers.database_controller import SessionLocal, engine
from controllers.authentication import require_master_password
from models.base import Base
from models.users import User


@click.command(name="create-admin")
@require_master_password
def create_admin():
    """Créer un utilisateur admin initial via mot de passe maître."""
    session = SessionLocal()
    try:
        manager = UserManager(session)

        firstname = click.prompt("Prénom")
        lastname = click.prompt("Nom")
        email = click.prompt("Email")
        password = click.prompt("Mot de passe", hide_input=True, confirmation_prompt=True)

        user = manager._create_admin_raw(firstname=firstname, lastname=lastname, email=email, password=password)
        click.secho(f"Administrateur {user.email} créé avec succès !", fg="green")
    except Exception as e:
        click.secho(f"Erreur : {e}", fg="red")
    finally:
        session.close()


@click.command(name="reset-db")
@require_master_password
def reset_db():
    """Supprime et recrée toutes les tables de la base."""
    confirm = click.confirm("ATTENTION !! Cette opération va supprimer toutes les données. Continuer ?", default=False)
    if not confirm:
        click.echo("Opération annulée.")
        return

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    click.secho("Base de données réinitialisée avec succès.", fg="yellow")


@click.command(name="delete-users")
@require_master_password
def delete_users():
    """Supprime tous les utilisateurs."""
    session = SessionLocal()
    try:
        confirm = click.confirm("ATTENTION !! Supprimer tous les utilisateurs ?", default=False)
        if not confirm:
            click.echo("Opération annulée.")
            return
        session.query(User).delete()
        session.commit()
        click.secho("Tous les utilisateurs ont été supprimés.", fg="red")
    finally:
        session.close()
