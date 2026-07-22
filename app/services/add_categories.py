from sqlalchemy import select, func, insert

from database.base import Session
from database.models import Category

def add_categories(user, group, name):
    session = Session()

    try:
        clean_names = [item.strip().lower() for item in name]
        exists = select(Category).where(Category.group_id==group.id, func.lower(Category.name).in_(clean_names))
        item_exists = session.scalars(exists).all()

        existing_items = [item.name.lower() for item in item_exists]
        add_items = [item for item in name if item not in existing_items]

        if existing_items and not add_items:
            return existing_items, add_items, True

        bulk_data = [{"group_id": group.id, "created_by": user.id, "name": item.lower()} for item in add_items]
        session.execute(insert(Category), bulk_data)
        session.commit()
        return existing_items, add_items, False

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()
