from sqlalchemy import select, delete, func

from database.base import Session
from database.models import ShoppingItem

def remove_shopping(session, user, group, name):
    exists = select(ShoppingItem).where(ShoppingItem.group_id==group.id, func.lower(ShoppingItem.name).in_(name))
    item_exists = session.scalars(exists).all()
    if not item_exists:
        return item_exists, False

    to_delete = delete(ShoppingItem).where(ShoppingItem.group_id==group.id, func.lower(ShoppingItem.name).in_(name))
    session.execute(to_delete)
    deleted = [item.name for item in item_exists]
    return deleted, True

def remove_shopping_items(user, group, name):
    session = Session()

    try:
        shopping_item, item_exists = remove_shopping(session, user, group, name)
        if item_exists:
            session.commit()
            return shopping_item, item_exists
        return shopping_item, item_exists

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()
