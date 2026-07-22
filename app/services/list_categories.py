from sqlalchemy import select

from database.base import Session
from database.models import Category

def list_categories(user, group):
    session = Session()

    try:
        exists = select(Category).where(Category.group_id==group.id)
        categories = session.scalars(exists).all()
        if categories:
            return categories, True
        return categories, False
    except Exception:
        session.rollback()
        raise

    finally:
        session.close()
