import click
from controllers.event_controller import EventsManager
from controllers.utils import get_manager
from models.events import Event


@click.group()
def event():
    """
    Event management command group.

    Provides commands to create, list, update, and delete events.
    Supports role-based access for sales and support departments.
    """
    pass


@event.command()
@click.option("--name", prompt="Nom de l'événement")
@click.option("--start-date", prompt="Date de début (YYYY-MM-DD HH:MM)")
@click.option("--end-date", prompt="Date de fin (YYYY-MM-DD HH:MM)")
@click.option("--location", prompt="Lieu")
@click.option("--attendees", prompt="Nombre de participants", type=int)
@click.option("--notes", prompt="Notes")
@click.option("--contract-id", prompt="ID du contrat", type=int)
@click.option(
    "--support-id",
    prompt="ID du support (laisser vide si aucun)",
    default="",
    show_default=False,
    callback=lambda ctx, param, value: int(value) if value else None,
)
def create(name, start_date, end_date, location, attendees, notes, contract_id, support_id):
    """
    Create a new event (Sales only).

    Required information includes the event name, date/time, location,
    attendees, notes, and the associated contract. Assigning a support
    user is optional.

    Raises:
        Exception: If any validation or permission check fails.
    """
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
    """
    List all events (accessible to authorized users).

    Displays each event's ID, name, start date, location, contract ID,
    and assigned support contact (if any).
    """
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
    """
    List events without an assigned support user (Management only).

    Useful for support managers to view unassigned tasks and delegate
    accordingly.
    """
    manager, session = get_manager(EventsManager)
    try:
        events = manager.get_unassigned_support_events()
        for e in events:
            click.echo(f"[{e.id}] {e.event_name} - {e.start_date} à {e.location}")
    finally:
        session.close()


@event.command(name="list-my")
def list_my_events():
    """
    List events assigned to the authenticated support user.

    Only available to users with the SUPPORT role.
    """
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
    """
    Update an event's details.

    Allows updating the location, attendees count, notes, or support contact.
    Permissions depend on user role:
    - SUPPORT users can update only their own events.
    - ACCOUNTING can update all events.

    Raises:
        Exception: If the user lacks permission or inputs are invalid.
    """
    manager, session = get_manager(EventsManager)
    try:
        # Rassembler les champs de mise à jour, en filtrant ceux à None
        values = {
            "location": location,
            "attendees": attendees,
            "notes": notes,
            "support_contact_id": support_id,
        }
        # Nettoyer les champs non fournis
        values = {k: v for k, v in values.items() if v is not None}

        if not values:
            click.secho("Aucune donnée à mettre à jour.", fg="yellow")
            return

        manager.update(Event.id == int(event_id), **values)
        click.secho("Événement mis à jour avec succès.", fg="green")
    except Exception as e:
        click.secho(str(e), fg="red")
    finally:
        session.close()


@event.command()
@click.option("--event-id", prompt="ID de l'événement")
def delete(event_id):
    """
    Delete an event (requires proper permissions).

    Only support staff can delete their own events. ACCOUNTING can delete
    any event.

    Raises:
        Exception: If unauthorized or deletion fails.
    """
    manager, session = get_manager(EventsManager)
    try:
        manager.delete(Event.id == int(event_id))
        click.secho(f"Événement {event_id} supprimé.", fg="yellow")
    except Exception as e:
        click.secho(str(e), fg="red")
    finally:
        session.close()
