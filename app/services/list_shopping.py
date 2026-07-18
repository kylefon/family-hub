from sqlalchemy import select

from database.base import Session
from database.models import ShoppingItem

def list_shopping(session, user, group):
    exists = select(ShoppingItem).where(ShoppingItem.group_id==group.id)
    shopping_item = session.scalars(exists).all()
    if shopping_item:
        return shopping_item, True
    return shopping_item, False

def list_shopping_items(user, group):
    session = Session()

    try:
        shopping_item, items_exists = list_shopping(session, user, group)
        if items_exists:
            return shopping_item, items_exists
        return shopping_item, items_exists

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()
