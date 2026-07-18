from sqlalchemy import select

from database.base import Session
from database.models import User, Group, GroupMember

def get_or_create_user(session, effective_user):
    existing = select(User).where(User.telegram_id==effective_user.id)
    row_exists = session.scalar(existing)
    if row_exists:
        return row_exists
    db_user = User(telegram_id=effective_user.id, username=effective_user.first_name)
    session.add(db_user)
    return db_user

def get_or_create_group(session, effective_chat):
    existing = select(Group).where(Group.telegram_chat_id==effective_chat.id)
    row_exists = session.scalar(existing)
    if row_exists:
        return row_exists
    if effective_chat.type == 'private':
        group_name = effective_chat.first_name
    else:
        group_name = effective_chat.title
    db_group = Group(telegram_chat_id=effective_chat.id, name=group_name, group_type=effective_chat.type)
    session.add(db_group)
    return db_group

def get_or_create_group_member(session, user, group):
    existing = select(GroupMember).where(GroupMember.group_id==group.id, GroupMember.user_id==user.id)
    row_exists = session.scalar(existing)
    if row_exists:
        return row_exists
    db_members = GroupMember(group_id=group.id, user_id=user.id)
    session.add(db_members)
    return db_members

def initialize_context(effective_user, effective_chat):
    session = Session()

    try:
        user = get_or_create_user(session, effective_user)

        if not user.is_allowed:
            session.commit()
            return user, None

        group = get_or_create_group(session, effective_chat)
        session.flush()
        get_or_create_group_member(session, user, group)
        session.commit()
        return user, group

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()
