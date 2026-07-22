from sqlalchemy import select, delete, func

from database.base import Session
from database.models import Category

def remove_categories(user, group, name):
    session = Session()

    try:
        exists = select(Category).where(Category.group_id==group.id, func.lower(Category.name).in_(name))
        item_exists = session.scalars(exists).all()
        if not item_exists:
            return item_exists, False

        to_delete = delete(Category).where(Category.group_id==group.id, func.lower(Category.name).in_(name))
        session.execute(to_delete)
        session.commit()
        deleted = [item.name for item in item_exists]
        return deleted, True

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()
