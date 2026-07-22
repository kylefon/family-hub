from sqlalchemy import select, func, insert

from database.base import Session
from database.models import Reminder

import dateparser

def add_reminder_item(session, user, group, reminder):
    message = "\n".join(reminder[1:-1]).lower()
    settings = {
        "TIMEZONE": "Asia/Manila",
        "RETURN_AS_TIMEZONE_AWARE": True,
        "PREFER_DATES_FROM": "future",
    }

    reminder_time = dateparser.parse(reminder[-1], languages=['en', 'tl'], settings=settings)

    #print(f"FULL REMINDER: {reminder}")
    exists = select(Reminder).where(Reminder.group_id==group.id, Reminder.text==message, Reminder.remind_at==reminder_time)
    item_exists = session.scalar(exists)

    print(f"existing items: {item_exists}")

    if item_exists:
        return reminder_time, message, True
    #print(f"TIME: {reminder_time} REMINDER: {message} Assigned to {user.id}")
    db_reminder = Reminder(group_id=group.id, created_by=user.id,assigned_to=user.id,text=message,remind_at=reminder_time)
    session.add(db_reminder)
    return reminder_time, message, False

def add_reminder(user, group, reminder):
    session = Session()

    try:
        reminder_time, message, item_exists = add_reminder_item(session, user, group, reminder)
        if item_exists:
            return  reminder_time, message, item_exists
        session.commit()
        return reminder_time, message, item_exists

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()
