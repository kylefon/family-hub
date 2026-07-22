from sqlalchemy import select

from database.base import Session
from database.models import Reminder

def list_reminders(user, group):
    session = Session()

    try:
        exists = select(Reminder).where(Reminder.group_id==group.id)
        reminders = session.scalars(exists).all()

        if reminders:
            return reminders, True
        return reminders, False

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()
