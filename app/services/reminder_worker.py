from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from sqlalchemy import select, delete

from database.base import Session
from database.models import Reminder, Group

def delete_reminder(reminder_id):
    session = Session()

    try:
        query = delete(Reminder).where(Reminder.id == reminder_id)
        session.execute(query)
        session.commit()

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def get_group_id(group_id):
    session = Session()
    try:
        query = select(Group).where(Group.id==group_id)
        group_row = session.scalar(query)

        return group_row.telegram_chat_id

    except Exception:
        session.rolback()
        raise
    finally:
        session.close()

def get_due_reminders():
    session = Session()

    try:
        query = select(Reminder).where(Reminder.remind_at <= datetime.now(ZoneInfo("Asia/Manila")), Reminder.is_done == False, Reminder.is_deleted == False)
        #group_query = select(Group).where(Group.id==Reminder.group_id)
        reminders = session.scalars(query).all()
        #group_row = session.scalar(group_query)

        return reminders

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()
