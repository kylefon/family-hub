
from sqlalchemy import select, delete, func

from database.base import Session
from database.models import Reminder

def remove_reminder(group, name):
    session = Session()

    try:
        exists = select(Reminder).where(Reminder.group_id==group.id, func.lower(Reminder.text).in_(name))
        item_exists = session.scalars(exists).all()

        if not item_exists:
            return item_exists, False

        to_delete = delete(Reminder).where(Reminder.group_id==group.id, func.lower(Reminder.text).in_(name))

        session.execute(to_delete)
        deleted = [item.text for item in item_exists]
        session.commit()
        return deleted, True
    except Exception:
        session.rollback()
        raise

    finally:
        session.close()
