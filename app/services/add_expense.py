from sqlalchemy import select, func, insert

from database.base import Session
from database.models import ShoppingItem

def add_shopping(session, user, group, name):
    clean_names = [item.strip().lower() for item in name]
    exists = select(ShoppingItem).where(ShoppingItem.group_id==group.id, func.lower(ShoppingItem.name).in_(clean_names))
    item_exists = session.scalars(exists).all()


    existing_items = [item.name.lower() for item in item_exists]
    add_items = [item for item in name if item not in existing_items]

    #print(f"existing items: {existing_items}")
    #print(f"items that will be added: {add_items}")

    if existing_items and not add_items:
        return existing_items, add_items, True

    bulk_data = [{"group_id": group.id, "added_by": user.id, "name": item.lower(), "is_done": False} for item in add_items]
    session.execute(insert(ShoppingItem), bulk_data)
    return existing_items, add_items, False

def add_shopping_item(user, group, name):
    session = Session()

    try:
        existing_items, add_items, item_exists = add_shopping(session, user, group, name)
        if item_exists:
            return  existing_items, add_items, item_exists
        session.commit()
        return  existing_items, add_items, item_exists

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()
