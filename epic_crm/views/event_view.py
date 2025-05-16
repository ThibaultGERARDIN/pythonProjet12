import click
from controllers.event_controller import EventsManager
from controllers.utils import get_manager
from models.events import Event


@click.group()
def event():
    """Commandes de gestion des événements."""
    pass


@event.command()
@click.option("--name", prompt="Nom de l'événement")
@click.option("--start-date", prompt="Date de début (YYYY-MM-DD HH:MM)")
@click.option("--end-date", prompt="Date de fin (YYYY-MM-DD HH:MM)")
@click.option("--location", prompt="Lieu")
@click.option("--attendees", prompt="Nombre de participants", type=int)
@click.option("--notes", prompt="Notes")
@click.option("--contract-id", prompt="ID du contrat", type=int)
@click.option("--support-id", type=int, required=False)
def create(name, start_date, end_date, location, attendees, notes, contract_id, support_id):
    """Créer un événement (réservé aux commerciaux). Le support est facultatif."""
    manager, session = get_manager(EventsManager)
    try:
        from datetime import datetime

        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)

        kwargs = {
            "event_name": name,
            "start_date": start_dt,
            "end_date": end_dt,
            "location": location,
            "attendees": attendees,
            "notes": notes,
            "contract_id": contract_id,
        }
        if support_id is not None:
            kwargs["support_contact_id"] = support_id

        event = manager.create(**kwargs)
        event.event_name = name
        session.commit()

        click.secho(f"Événement créé (ID: {event.id})", fg="green")
    except Exception as e:
        click.secho(str(e), fg="red")
    finally:
        session.close()


@event.command()
def list():
    """Lister tous les événements (pour les autorisés)"""
    manager, session = get_manager(EventsManager)
    try:
        events = manager.get_all()
        for e in events:
            click.echo(
                f"[{e.id}] {e.event_name} - {e.start_date} à {e.location} "
                f"(Contrat #{e.contract_id}, Support: {e.support_contact_id})"
            )
    finally:
        session.close()


@event.command(name="list-unassigned")
def list_unassigned():
    """Lister les événements sans support assigné (gestion uniquement)"""
    manager, session = get_manager(EventsManager)
    try:
        events = manager.get_unassigned_support_events()
        for e in events:
            click.echo(f"[{e.id}] {e.event_name} - {e.start_date} à {e.location}")
    finally:
        session.close()


@event.command(name="list-my")
def list_my_events():
    """Lister les événements dont je suis responsable (support uniquement)"""
    manager, session = get_manager(EventsManager)
    try:
        events = manager.get_my_events()
        for e in events:
            click.echo(f"[{e.id}] {e.event_name} - {e.start_date} à {e.location}")
    finally:
        session.close()


@event.command()
@click.option("--event-id", prompt="ID de l'événement")
@click.option("--location", default=None)
@click.option("--attendees", type=int, default=None)
@click.option("--notes", default=None)
@click.option("--support-id", type=int, default=None)
def update(event_id, location, attendees, notes, support_id):
    """Modifier un événement (support ou gestion selon les droits)"""
    manager, session = get_manager(EventsManager)
    try:
        values = {}
        if location:
            values["location"] = location
        if attendees:
            values["attendees"] = attendees
        if notes:
            values["notes"] = notes
        if support_id:
            values["support_contact_id"] = support_id

        manager.update(Event.id == int(event_id), **values)
        click.secho("Événement mis à jour avec succès.", fg="green")
    except Exception as e:
        click.secho(str(e), fg="red")
    finally:
        session.close()


@event.command()
@click.option("--event-id", prompt="ID de l'événement")
def delete(event_id):
    """Supprimer un événement (selon les permissions)"""
    manager, session = get_manager(EventsManager)
    try:
        manager.delete(Event.id == int(event_id))
        click.secho(f"Événement {event_id} supprimé.", fg="yellow")
    except Exception as e:
        click.secho(str(e), fg="red")
    finally:
        session.close()
